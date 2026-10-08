"""Campus Customs API (FastAPI). Run from the backend/ folder:

    uvicorn main:app --reload --port 8000

Accounts (Problem 4) use the existing `users` table in data/campus_customs.db:
    POST /api/auth/signup   {first_name, last_name, email, password} -> creates the account and logs in
    POST /api/auth/login    {email, password}                         -> logs in
    POST /api/auth/logout                                             -> logs out
    GET  /api/auth/me                                                 -> the logged-in user, or 401
Responses only ever contain id, first/last name, name and email: never password hashes.

Chatbot (Problems 5-8):
    POST /api/chat          {message, history, current_product_id} -> {reply, products, current_product_id, saved}
    GET  /api/chat/history                                           -> the logged-in user's saved messages (401 for guests)
Logged-in conversations are saved to chat_messages; guest conversations are not.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from pathlib import Path

from fastapi import Cookie, FastAPI, HTTPException, Response
from pydantic_ai.exceptions import UsageLimitExceeded

import agent
import audit
import auth
import tools
from models import (
    ChatContext,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatTurn,
    HistoryMessage,
    LoginRequest,
    PublicUser,
    SignupRequest,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
HISTORY_TURNS = 20  # saved messages given to the agent as context
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
log = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _public(row: sqlite3.Row) -> PublicUser:
    # Older rows may lack first/last name; fall back to splitting `name`.
    first, _, last = row["name"].partition(" ")
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"] or first,
        last_name=row["last_name"] or last,
        name=row["name"],
        email=row["email"],
    )


def _start_session(response: Response, user_id: int) -> None:
    response.set_cookie(
        auth.SESSION_COOKIE,
        auth.make_session_token(user_id),
        max_age=auth.SESSION_MAX_AGE,
        httponly=True,  # JavaScript can't read it
        samesite="lax",
        path="/",
    )


# --- Accounts (Problem 4) ----------------------------------------------------


@app.post("/api/auth/signup", response_model=PublicUser, status_code=201)
def signup(body: SignupRequest, response: Response) -> PublicUser:
    email = body.email.strip().lower()
    first, last = body.first_name.strip(), body.last_name.strip()
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if not first or not last:
        raise HTTPException(400, "Please enter your first and last name.")
    with _db() as con:
        if con.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise HTTPException(409, "An account with this email already exists.")
        try:
            cur = con.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", email, auth.hash_password(body.password), first, last),
            )
        except sqlite3.IntegrityError:  # UNIQUE(email) in the database
            raise HTTPException(409, "An account with this email already exists.") from None
        row = con.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    _start_session(response, row["id"])
    return _public(row)


@app.post("/api/auth/login", response_model=PublicUser)
def login(body: LoginRequest, response: Response) -> PublicUser:
    with _db() as con:
        row = con.execute("SELECT * FROM users WHERE lower(email) = ?", (body.email.strip().lower(),)).fetchone()
    if row is None or not auth.verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Incorrect email or password.")  # same message either way
    _start_session(response, row["id"])
    return _public(row)


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(auth.SESSION_COOKIE, path="/")


def _current_user(cc_session: str | None) -> sqlite3.Row | None:
    """The logged-in user's row, from the signed session cookie only (never from the request body)."""
    user_id = auth.read_session_token(cc_session)
    if user_id is None:
        return None
    with _db() as con:
        return con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@app.get("/api/auth/me", response_model=PublicUser)
def me(cc_session: str | None = Cookie(default=None)) -> PublicUser:
    row = _current_user(cc_session)
    if row is None:
        raise HTTPException(401, "Not logged in.")
    return _public(row)


# --- Chatbot (Problems 5-8) ----------------------------------------------------


def _saved_turns(user_id: int, after_id: int = 0, limit: int = HISTORY_TURNS) -> list[ChatTurn]:
    """The user's most recent saved messages (oldest first) - only rows with this user_id.

    `after_id` is the "New chat" boundary: earlier messages stay saved but aren't used as context.
    """
    with _db() as con:
        rows = con.execute(
            "SELECT role, content FROM chat_messages WHERE user_id = ? AND id > ? ORDER BY id DESC LIMIT ?",
            (user_id, after_id, limit),
        ).fetchall()
    return [ChatTurn(role=r["role"], content=r["content"]) for r in reversed(rows) if r["role"] in ("user", "assistant")]


def _save_exchange(user_id: int, message: str, reply: str, product_ids: list[str]) -> int:
    """Save the customer's message and the assistant's reply together (one transaction)."""
    with _db() as con:
        con.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, message),
        )
        cur = con.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply, json.dumps(tools.product_snapshots(product_ids))),
        )
        return cur.lastrowid


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    """Answer one customer message with the PydanticAI agent.

    Logged in: history comes from chat_messages and the exchange is saved there.
    Guest: history comes from the browser (this visit only) and nothing is saved.
    """
    user = _current_user(cc_session)
    product = tools.validate_product(body.current_product_id)  # unknown IDs are ignored, never trusted
    context = ChatContext(logged_in=user is not None, first_name=_public(user).first_name if user else None, current_product=product)
    turns = _saved_turns(user["id"], body.history_after_id or 0) if user else body.history
    entry = {
        "event": "chat",
        "customer": {"user_id": user["id"]} if user else "guest",  # id from the session cookie only; no email/hash
        "message": audit.redact(body.message),
        "current_product": {
            "requested": audit.redact(body.current_product_id or "", 100) or None,
            "validated": product.product_id if product else None,
            "rejected": bool(body.current_product_id) and product is None,
        },
        "history_turns": len(turns),
        "model": agent.MODEL_NAME,
        "limits": {"model_requests": agent.MAX_MODEL_REQUESTS, "tool_calls": agent.MAX_TOOL_CALLS},
    }
    try:
        run = await agent.chat(body.message, turns, context)
    except Exception as exc:
        run = getattr(exc, "chat_run", None)
        if isinstance(exc, UsageLimitExceeded):
            status, detail = 503, "That question needed too many steps. Please ask something more specific."
        elif isinstance(exc, RuntimeError):  # e.g. PORTKEY_API_KEY missing
            status, detail = 503, "The shopping assistant is unavailable right now."
        else:  # model/provider failure; never echo provider details or secrets
            status, detail = 502, "The shopping assistant couldn't answer just now. Please try again."
        log.error("chat failed: %s", type(exc).__name__)
        audit.record({
            **entry,
            "steps": audit.agent_steps(run.messages) if run else [],
            "usage": {"model_requests": run.usage.requests, "tool_calls": run.usage.tool_calls} if run else None,
            "outcome": {"status": "usage_limit_exceeded" if isinstance(exc, UsageLimitExceeded) else "error",
                        "http_status": status, "error": type(exc).__name__, "detail": audit.redact(str(exc), 200)},
        })
        raise HTTPException(status, detail) from None
    reply = run.output
    last_id = _save_exchange(user["id"], body.message, reply.reply, reply.product_ids) if user else None
    cards = tools.product_cards(reply.product_ids)  # cards come from the database, so only real products/prices
    audit.record({
        **entry,
        "steps": audit.agent_steps(run.messages),
        "usage": {"model_requests": run.usage.requests, "tool_calls": run.usage.tool_calls},
        "outcome": {"status": "ok", "http_status": 200, "reply": audit.redact(reply.reply),
                    "product_ids": [c.product_id for c in cards], "saved_to_history": user is not None},
    })
    return ChatResponse(
        reply=reply.reply,
        products=cards,
        current_product_id=product.product_id if product else None,
        saved=user is not None,
        last_message_id=last_id,
    )


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def chat_history(cc_session: str | None = Cookie(default=None)) -> ChatHistoryResponse:
    """The logged-in user's own saved conversation, with product cards rebuilt from products_json."""
    user = _current_user(cc_session)
    if user is None:
        raise HTTPException(401, "Log in to see your saved chat history.")
    with _db() as con:
        rows = con.execute(
            "SELECT id, role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id",
            (user["id"],),
        ).fetchall()
    messages = []
    for r in rows:
        ids = []
        if r["products_json"]:
            try:
                ids = [p["product_id"] for p in json.loads(r["products_json"]) if isinstance(p, dict) and "product_id" in p]
            except (ValueError, TypeError):
                ids = []
        messages.append(
            HistoryMessage(
                id=r["id"],
                role=r["role"], content=r["content"], products=tools.product_cards(ids), created_at=r["created_at"]
            )
        )
    return ChatHistoryResponse(messages=messages)
