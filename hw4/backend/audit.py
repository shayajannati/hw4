"""Append-only audit trail of chatbot agent activity: output/audit_trail.json.

Format: one valid JSON array, one object per chat request (one PydanticAI agent run).

Append-only: a new record is written by replacing ONLY the closing "]" at the very end
of the file with ",\\n<record>\\n]". Earlier bytes are never rewritten, reordered or
deleted, and the file is valid JSON after every write. Writes hold an exclusive lock
(fcntl), so concurrent requests can't interleave. If the file is ever not a JSON array
that ends in "]", it is kept unchanged (renamed *.corrupt-<time>.json) and a new trail
is started, so damaged history is preserved rather than overwritten.

Never recorded: API keys / Portkey credentials, password hashes, session cookies or
secrets, email addresses. Free text (customer message, tool args/results, reply) is
shortened and passed through `redact()` as a second line of defence.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart

AUDIT_PATH = Path(os.getenv("AUDIT_TRAIL_PATH", Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"))
TEXT_CHARS = 300  # customer message / reply
ARG_CHARS = 200  # tool arguments
RESULT_CHARS = 300  # tool results

_SECRET_PATTERNS = [
    (re.compile(r"pbkdf2_sha256\$[^\s\"']+"), "[redacted-password-hash]"),
    (re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_\-]{12,}"), "[redacted-key]"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{12,}"), "[redacted-token]"),
    (re.compile(r"cc_session=[^\s;\"']+"), "cc_session=[redacted]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[redacted-email]"),
]


def _secret_values() -> list[str]:
    """Live secret values from the environment, so they can never be written even if echoed."""
    vals = [os.getenv(k, "").strip() for k in ("PORTKEY_API_KEY", "SESSION_SECRET")]
    secret_file = Path(__file__).resolve().parent / ".session_secret"
    if secret_file.exists():
        vals.append(secret_file.read_text().strip())
    return [v for v in vals if len(v) >= 8]


def redact(text: Any, limit: int = TEXT_CHARS) -> str:
    # Tool results are often Pydantic models: store them as JSON, not Python's repr.
    s = text if isinstance(text, str) else json.dumps(to_jsonable_python(text, fallback=str), ensure_ascii=False)
    for value in _secret_values():
        s = s.replace(value, "[redacted-secret]")
    for pattern, repl in _SECRET_PATTERNS:
        s = pattern.sub(repl, s)
    s = " ".join(s.split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def agent_steps(messages: list[ModelMessage]) -> list[dict[str, Any]]:
    """One entry per agent-loop iteration (model response): time, tool calls with short args/results, stop reason."""
    returns: dict[str, Any] = {}
    for m in messages:
        if isinstance(m, ModelRequest):
            for p in m.parts:
                if isinstance(p, (ToolReturnPart, RetryPromptPart)) and p.tool_call_id:
                    returns[p.tool_call_id] = p
    steps = []
    for m in messages:
        if not isinstance(m, ModelResponse):
            continue
        calls = []
        for p in m.parts:
            if not isinstance(p, ToolCallPart):
                continue
            ret = returns.get(p.tool_call_id)
            if isinstance(ret, RetryPromptPart):
                result = "rejected: " + redact(ret.content, RESULT_CHARS)
            elif isinstance(ret, ToolReturnPart):
                result = redact(ret.content, RESULT_CHARS) if p.tool_name != "final_result" else "final answer accepted"
            else:
                result = "(no result recorded)"
            calls.append({"tool": p.tool_name, "args": redact(p.args_as_json_str(), ARG_CHARS), "result": result})
        steps.append(
            {
                "time": m.timestamp.astimezone(timezone.utc).isoformat(timespec="seconds"),
                "tool_calls": calls,
                "stop_reason": m.finish_reason or "unknown",
            }
        )
    return steps


def record(entry: dict[str, Any], path: Path | None = None) -> None:
    """Append one record. Never rewrites existing records."""
    path = Path(path) if path is not None else AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps({"time": _now(), **entry}, ensure_ascii=False, indent=2)
    with open(path, "a+b") as f:  # append mode: every write lands at the end of the file
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            size = f.seek(0, os.SEEK_END)
            if size == 0:
                f.write(("[\n" + blob + "\n]\n").encode())
                return
            f.seek(0)
            first = f.read(1)
            f.seek(max(0, size - 4096))
            tail = f.read()
            body = tail.rstrip()
            if first != b"[" or not body.endswith(b"]"):
                raise ValueError("audit trail is not a JSON array")
            close_at = size - len(tail) + len(body) - 1  # byte offset of the final "]"
            empty = body[:-1].rstrip().endswith(b"[")  # "[]": no comma before the first record
            f.truncate(close_at)  # removes only the closing bracket and trailing whitespace
            f.write((("" if empty else ",") + "\n" + blob + "\n]\n").encode())
        except ValueError:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            path.replace(path.with_name(f"{path.stem}.corrupt-{stamp}{path.suffix}"))  # keep, never overwrite
            path.write_text("[\n" + blob + "\n]\n", encoding="utf-8")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
