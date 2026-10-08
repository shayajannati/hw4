# Harness — Homework 4: the Campus Customs storefront and shopping assistant

This file has two parts:

- **Part 1 (final reference)** describes the finished system: how to run it, the
  model and agent, the tools, the data models, the safety rules, the execution limits
  and the audit trail.
- **Part 2** keeps the problem-by-problem build notes and test results (Problems 2–10).

---

# Part 1: Final technical reference (Problem 12)

## 1. Overview

```
React + Vite + TypeScript storefront (frontend/)        FastAPI backend (backend/main.py)
  product grid · search · product pages · login   /api   auth (users table, PBKDF2, signed cookie)
  chat widget with dynamic product cards        ───────► POST /api/chat ─► PydanticAI agent (backend/agent.py)
                                                            │                 │ tools (backend/tools.py, read-only SQLite)
                                                            │                 ▼
                                                            │          data/campus_customs.db
                                                            ├─► chat_messages (logged-in history)
                                                            └─► output/audit_trail.json (append-only)
```

The storefront's product data is exported read-only from `data/campus_customs.db` into
`frontend/public/` by `scripts/export_catalogue.py`, which runs automatically before
`npm run dev` and `npm run build`.

## 2. Install and run from a fresh checkout

These commands were verified on a fresh copy of `hw4/` without `.venv`,
`node_modules`, generated files or secrets: the storefront loaded, the catalogue was
exported, login worked through the proxy, and chat answered 503 safely when no API key
was present.

**Prerequisites:** Python 3.12+ (tested on 3.14), Node.js 20+ (tested on 24), and the
course `data/` folder inside `hw4/`.

```bash
# from hw4/
cp .env.example .env            # then put your Portkey key in .env
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend && npm ci && cd ..
```

Run the two parts in **two terminals**:

```bash
# terminal 1: backend (from the backend/ folder, as the assignment requires)
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

```bash
# terminal 2: storefront
cd frontend
npm run dev                     # prints http://localhost:5173
```

Open the URL Vite prints.

- **Ports:** backend 8000, storefront 5173 (Vite's default). The storefront forwards
  every `/api/...` request to `http://127.0.0.1:8000` (`frontend/vite.config.ts`).
- **If port 8000 is busy:** run uvicorn with `--port <other>` and start the frontend
  with `API_PORT=<other> npm run dev`.
- **Directories used at run time:**
  - `data/campus_customs.db` (catalogue, inventory, users, chat history);
  - `data/products/` (photos, copied to `frontend/public/products/`);
  - `output/audit_trail.json` (created automatically).

## 3. Environment variables (`.env.example`)

`.env.example` lists the variables with placeholder values only. Copy it to `hw4/.env`;
the backend also reads the shared `AI Class/.env`. `.env` is git-ignored, and no real
secret appears in this repository or this file.

| Variable | Required | Purpose |
|---|---|---|
| `PORTKEY_API_KEY` | yes, for chat | Portkey key used for every model call |
| `PORTKEY_BASE_URL` | no (default `https://api.portkey.ai/v1`) | Portkey gateway URL |
| `MODEL_NAME` | no (default `gpt-5.6-luna`) | model used by the agent |
| `SESSION_SECRET` | no | signs login cookies; if unset, a random one is created once in `backend/.session_secret` (git-ignored) |
| `AUDIT_TRAIL_PATH` | no (default `output/audit_trail.json`) | used by tests to write a temporary audit file |
| `API_PORT` (frontend) | no (default 8000) | backend port for the Vite proxy |

## 4. Model and agent configuration (`backend/agent.py`)

- **Framework:** **PydanticAI** 2.54 `Agent`, which runs the model and tool loop
  itself; there is no hand-written loop.
- **Model:** **`gpt-5.6-luna`** via `OpenAIResponsesModel` on an `AsyncOpenAI` client
  pointed at the **Portkey** gateway (`x-portkey-api-key` header), with a 60 s timeout
  per model request.
- **Agent settings:**
  - `deps_type=ChatContext`;
  - `output_type=ChatReply`;
  - `instructions` = `backend/prompts/prompt.md`, plus a dynamic "Current customer
    context" instruction built from the validated context;
  - `tools=[search_products, resolve_product, get_product_details, check_inventory]`;
  - `retries=1`.
- **Lazy start:** the agent is built on the first chat request, so the server and
  login work without a key. Chat then answers 503.

## 5. Agent tools (`backend/tools.py`): all read-only

Every tool opens SQLite as `file:...campus_customs.db?mode=ro`, so any write fails with
"attempt to write a readonly database"; this was tested. The tools only run `SELECT`
statements, and no tool can change products, stock, users or history.

| Tool | Reads | Returns | What it's for |
|---|---|---|---|
| `search_products(query, limit=8)` | `catalogue` | `SearchResults` | Keyword search over name, garment type, description, colors and tags. Very common words (e.g. "yale") can't create a match on their own. When nothing matches, returns real garment types as `suggestions`. |
| `resolve_product(reference)` | `catalogue` | `ProductResolution` | Is "the dad one" one product (`unique`), several (`ambiguous`, with real candidates) or none (`not_found`)? Used before price or stock lookups. |
| `get_product_details(product_id)` | `catalogue` | `ProductDetails` or `NotFound` | The authoritative **price**, plus description, colors and garment type. |
| `check_inventory(product_id, size=None)` | `catalogue`, `inventory` | `InventoryResult` or `NotFound` | The exact **quantity** for one size, or for all sizes; `in_stock` is false at 0. Size words like "medium" and "2XL" are mapped to real sizes. |

`main.py` also uses these read-only helpers, which are **not** agent tools:
`validate_product` (checks the current-page product), `product_cards` (database rows
for the card IDs) and `product_snapshots` (`products_json` for saved history).

## 6. Data models (`backend/models.py`) and why these fields

| Model | Fields | Why |
|---|---|---|
| `SignupRequest`, `LoginRequest` | first/last name, email, password (8–200 chars) | validated input for accounts in the existing `users` table |
| `PublicUser` | `id`, `first_name`, `last_name`, `name`, `email` | the only user fields ever sent to the browser; never the password hash |
| `ChatTurn`, `ChatRequest` | `message` (≤2000 chars), `history` (≤20 turns, guests only), `current_product_id`, `history_after_id` | one customer message plus the context the server is allowed to consider; identity is **not** a field (it comes from the cookie) |
| `ProductSummary` | `product_id`, `name`, `garment_type`, `colors` | enough to tell products apart and pick one; no price or stock, so the model must fetch those from the authoritative tools |
| `SearchResults` | `query`, `matches`, `ignored_words`, `suggestions` | makes "no match" explicit and offers real alternatives, so the model has no reason to invent any |
| `ProductResolution` | `status`, `product`, `candidates` | an explicit unique/ambiguous/not-found signal, so the agent asks rather than picking a product |
| `ProductDetails` | `product_id`, `name`, `garment_type`, `description`, `colors`, `price` | the authoritative row for one product; `price` is the unrounded database value |
| `InventoryResult` / `SizeStock` | `product_id`, `name`, `sizes[size, quantity, in_stock]` | `size` and `quantity` are copied straight from `inventory`; `in_stock` makes "out of stock" explicit, so 0 can't be misread |
| `NotFound` | `error`, `valid_sizes` | an honest error for unknown products or sizes, with the real alternatives |
| `ChatReply` | `reply`, `product_ids` | the agent's structured output; it only *names* products, and the server builds the cards |
| `ProductCard`, `ChatResponse` | card: `product_id`, `name`, `garment_type`, `image`, `price`; response: `reply`, `products`, `current_product_id`, `saved`, `last_message_id` | cards are built from the database, so a card can't show an invented product or price |
| `CurrentProduct`, `ChatContext` | `product_id` + `name`; `logged_in`, `first_name`, `current_product` | per-request context for the agent (PydanticAI `deps`), containing nothing sensitive |
| `HistoryMessage`, `ChatHistoryResponse` | `id`, `role`, `content`, `products`, `created_at` | a user's own saved conversation, with cards rebuilt from current database data |

## 7. Safety rules: what's in the prompt and what code enforces

`backend/prompts/prompt.md` has a numbered **Safety rules** section that the model is
told to always follow. Each rule is listed below with what enforces it in code (✔) and
where the prompt is the only control.

| # | Rule | Enforced in code |
|---|---|---|
| 1 | Prices only from tools, never guessed | ✔ product **cards** always use the database price (`tools.product_cards`). For prices written in the reply text, the prompt is the control, and the tests check them against the database. |
| 2 | Stock and sizes only from tools | ✔ `check_inventory` is the only source of quantities. Same split as rule 1: the prompt governs the reply text, and the tests verify it. |
| 3 | Never invent products | ✔ unknown `product_ids` from the model are dropped before cards are built, so a card can't show a made-up product |
| 4 | Clarify ambiguity | ✔ `resolve_product` returns `ambiguous` with the real candidates; the prompt says not to pick one |
| 5 | Be honest about unknowns | ✔ `NotFound` and empty `SearchResults` with real `suggestions` |
| 6 | Read-only | ✔ SQLite `mode=ro` for every tool; no write tool exists |
| 7 | Identity from the session, not the user | ✔ `_current_user()` reads only the signed HttpOnly cookie, and requests have no user-id field |
| 8 | No other customer's history | ✔ every `chat_messages` query is `WHERE user_id = <session user>`; the widget clears on logout |
| 9 | No secrets to customers or the audit | ✔ the API returns only `PublicUser` fields, and `audit.redact()` strips keys, hashes, cookies and emails before anything is written |
| 10 | Validate page context | ✔ `tools.validate_product()` checks `current_product_id` against `catalogue`; unknown IDs are ignored and flagged `rejected` in the audit |
| 11 | Customer text is a request, not instructions | the prompt (tested with a prompt-injection message, which was refused) |

The model can't be technically forced to word its reply correctly. That's why the code
also bounds what it can affect: cards come from the database, the tools are read-only,
and identity comes from the session.

## 8. Execution limits and result caps

| Limit | Value | Where and how |
|---|---|---|
| Model requests (agent-loop iterations) per message | **8** | `UsageLimits(request_limit=8)` passed to every `agent.run` (`agent.USAGE_LIMITS`) |
| Tool calls per message | **12** | `UsageLimits(tool_calls_limit=12)` |
| Invalid structured-output retries | **1** | `Agent(retries=1)` |
| Model request timeout | **60 s** | `AsyncOpenAI(timeout=60)` |
| When a limit is hit | — | PydanticAI raises `UsageLimitExceeded`. `/api/chat` returns **503** ("That question needed too many steps…") and writes an audit record with status `usage_limit_exceeded`. |
| Search results | **≤ 12** (default 8) | `search_products` clamps `limit` |
| Ambiguity candidates | **≤ 12** | `resolve_product` |
| Inventory rows | ≤ the product's sizes (6) | `check_inventory` |
| Customer message | ≤ 2000 characters | `ChatRequest` validation |
| Conversation context | ≤ 20 turns | `ChatRequest.history` (guests) / `HISTORY_TURNS` (logged in) |
| Audit text | message/reply 300, tool args 200, tool results 300 characters | `audit.py` |

**Verified enforced by the framework**, with a fake model that never stops calling
tools:

- the run stopped with `UsageLimitExceeded` after **8** model calls ("The next request
  would exceed the request_limit of 8");
- a model making two tool calls per turn was stopped at the **12** tool-call limit,
  with 12 tool calls executed;
- through the endpoint, the runaway run returned 503 and produced an audit record with
  all 8 steps.

## 9. Identity, history, guests and current-product context

- **Identity:** signup and login use the existing `users` table, with PBKDF2-SHA256
  (120,000 iterations, a random salt, the seeded format). After login the browser
  holds a signed, HttpOnly, 7-day `cc_session` cookie. The backend gets the customer
  only from that cookie; the agent receives only `logged_in` and the first name.
- **Logged-in history:**
  - each successful exchange (customer message + reply, with `products_json` in the
    seeded format) is saved to `chat_messages` under the session user;
  - the agent's context is that user's last 20 saved messages;
  - `GET /api/chat/history` returns only that user's messages, with cards rebuilt;
  - "New chat" sets a per-tab boundary (`history_after_id`). Nothing is deleted.
- **Guests:** chat works for the visit, with history sent from the widget. **Nothing is
  saved**, and `/api/chat/history` returns 401.
- **Current product:** the widget sends the `#/product/<id>` it's showing. The server
  validates it against `catalogue` before the agent sees it. "This" then means that
  product, and price and stock still come from the tools.

## 10. Audit trail: `output/audit_trail.json`

- **Format:** one valid JSON array. There is **one record per chat request** (one
  PydanticAI run), appended by `audit.record()` and called from `/api/chat` in
  `backend/main.py` on success **and** on error.
- **Each record contains:**
  - `time`, `event` (`"chat"`), and `customer` (`{"user_id": n}` from the session, or
    `"guest"`);
  - `message` (shortened and redacted);
  - `current_product` (`requested`, `validated`, `rejected`);
  - `history_turns`, `model`, `limits`;
  - `steps`, one per agent-loop iteration: `time`, `tool_calls[{tool, args, result}]`
    (shortened) and `stop_reason` (the model's finish reason);
  - `usage` (`model_requests`, `tool_calls`);
  - `outcome`: `status` (`ok` / `error` / `usage_limit_exceeded`), `http_status`, and
    either the redacted `reply`, `product_ids` and `saved_to_history`, or the `error`
    type and a redacted `detail`.
- **Append-only:**
  - the file is opened in append mode under an exclusive `fcntl` lock;
  - only the final closing `]` is removed, and `,<record>]` is written after it, so
    every earlier byte is left exactly as it was and the file is valid JSON after each
    write;
  - the trail is never cleared between runs;
  - a file that isn't a JSON array is renamed `audit_trail.corrupt-<time>.json` and
    kept, never overwritten.

  Tests confirmed earlier bytes were byte-identical after every append.
- **Never recorded:** API keys and Portkey credentials, the session secret, password
  hashes, cookies and email addresses. `redact()` removes the live key and session
  secret values, `pbkdf2_sha256$…`, `sk-…`, bearer tokens, `cc_session=…` and email
  addresses from any text before writing. A scan of the real trail found none of them.
- **Note:** the first 8 records (created while testing Problem 12) store tool results
  as Python text, from before a fix that now stores them as JSON. They were left
  unchanged because the trail is append-only.

## 11. Problem 12 test results

- **Offline (no model calls), all passed:**
  - the request limit (8) and tool-call limit (12) are enforced by PydanticAI;
  - the endpoint returns 503 and audits a limit hit;
  - the search and candidate caps (12) hold;
  - the tools' connection refuses writes, and the database is byte-identical
    afterwards;
  - the audit writer stays valid JSON after each append, never rewrites earlier bytes,
    redacts secrets, and handles an empty or corrupt file.
- **Live (`gpt-5.6-luna` through the running app):**
  - search, navy crewnecks: 11 cards, `search_products` audited;
  - price: Basic Hoodie Big Yale, $68.00, matching the database;
  - inventory: Yale Dad Hoodie size L, 20, matching the database;
  - ambiguous "tennis shirt": `resolve_product` returned ambiguous with 3 candidates,
    and no price was given;
  - unknown "unicorn cape": an honest no-match with no cards;
  - fake page product: ignored and flagged `rejected`;
  - prompt injection asking for another user's history, hashes and keys: refused;
  - logged-in "Do you have this in medium?" on `champion-reverse-weave-hoodie-1`: 20,
    matching the database, saved to history and attributed to `user_id 4`;
  - login and logout work, and guests saved 0 rows;
  - a browser smoke test passed: 102 products, search, chat cards opening the product
    page, and no page errors.
- **The trail:** valid JSON (10 records after testing); earlier records intact after
  every append; no secrets found.
- **Database rows added:** 2 `chat_messages` rows for test user 4. Seeded data is
  unchanged.

---

# Part 2: Problem-by-problem build notes

## Problem 2: Analyze the database

`data/campus_customs.db` is a SQLite database. It was inspected read-only (schema,
row counts and a few sample rows); nothing in it was changed.

It has **4 tables**: `catalogue`, `inventory`, `users` and `chat_messages`. SQLite
also keeps an internal `sqlite_sequence` table, which tracks the last auto-generated ID
for `inventory`, `users` and `chat_messages`. It isn't shop data.

```
users ──< chat_messages            (chat_messages.user_id → users.id)
catalogue ──< inventory            (inventory.product_id → catalogue.product_id)
```

### `catalogue`: what the shop sells (102 rows, one per product)

| Field | Type | What it's for |
|---|---|---|
| `product_id` | TEXT, primary key | Unique ID for the product (e.g. `basic-hoodie-big-yale`), matching its photo's filename. Every other table refers to products by this ID. |
| `name` | TEXT | Human-readable product name shown to customers (e.g. "Basic Hoodie Big Yale"). |
| `garment_type` | TEXT | The kind of item (e.g. crewneck sweatshirt, pullover hoodie). Lets the chatbot answer "what hoodies do you have?". |
| `description` | TEXT | A sentence describing the product's look; used to answer questions about a product and to match what a customer describes. |
| `colors` | TEXT (JSON list) | The product's colors, e.g. `["navy", "white"]`; answers color questions ("do you have this in pink?"). |
| `search_tags` | TEXT (JSON list) | Keywords such as "Yale", "baseball", "navy sweatshirt"; help find products from loosely worded requests. |
| `image_file_path` | TEXT | Path to the product photo, relative to `data/` (e.g. `products/basic-hoodie-big-yale.jpg`); lets the shop show the item. |
| `price` | REAL | Price in dollars; answers "how much is it?" and supports budgets. |

Notes from the data:

- Prices range from $32 to $98, with only 7 distinct prices. Products of the same
  kind share a price; for example, the hoodies in the sample chat are all $68.
- There are 22 distinct `garment_type` values. Some differ only in wording or
  capitalisation, e.g. "short-sleeve t-shirt" (16) vs "short-sleeve T-shirt" (6), and
  "quarter-zip pullover" vs "quarter-zip pullover sweatshirt". Searches should
  therefore not rely on exact matches.
- `colors` and `search_tags` are JSON text, so they must be parsed before use.
- All 102 product photos are listed, including `timothy-dwight-college-crewneck`.

### `inventory`: stock by size (612 rows)

| Field | Type | What it's for |
|---|---|---|
| `id` | INTEGER, primary key | Auto-generated row number. |
| `product_id` | TEXT → `catalogue.product_id` | Which product the stock count belongs to. |
| `size` | TEXT | Size: XS, S, M, L, XL or XXL. |
| `quantity` | INTEGER | Units in stock for that product and size; 0 means sold out in that size. Lets the chatbot say whether an item can be bought in the customer's size. |

Each `(product_id, size)` pair is unique. Every product has exactly 6 rows, one per
size (102 × 6 = 612), and there are no rows for products missing from the catalogue.
Quantities range from 0 to 25 (average 9.7). **145 of the 612 product-size combinations
are out of stock**, so stock has to be checked before suggesting a size.

### `users`: shop accounts (3 rows)

| Field | Type | What it's for |
|---|---|---|
| `id` | INTEGER, primary key | Auto-generated user ID; links a user to their chat history. |
| `name` | TEXT | Full display name. In every row it equals `first_name` + `last_name`. |
| `email` | TEXT, unique | Login identifier; no two accounts can share one. |
| `password_hash` | TEXT | The password stored as a salted PBKDF2-SHA256 hash (`pbkdf2_sha256$<salt>$<hash>`), never in plain text. Used to check logins. |
| `created_at` | TEXT | When the account was created (UTC, set automatically). |
| `first_name`, `last_name` | TEXT, nullable | Name split into parts, e.g. so the chatbot can greet the user by first name. These were added to the table after it was created (they appear at the end of the schema and are optional). |

The 3 accounts are a test user and two named users. Emails and password hashes are
personal and security data. They aren't reproduced here, and the chatbot should never
reveal them.

### `chat_messages`: chatbot conversation history (22 rows)

| Field | Type | What it's for |
|---|---|---|
| `id` | INTEGER, primary key | Auto-generated message ID; gives the order of messages. |
| `user_id` | INTEGER → `users.id` | Whose conversation the message belongs to, so each user sees only their own history. |
| `role` | TEXT | `user` (the customer's message) or `assistant` (the chatbot's reply). |
| `content` | TEXT | The message text; assistant replies use Markdown (e.g. bold prices). |
| `products_json` | TEXT (JSON), nullable | For assistant replies, the products referenced in the reply (product ID, name, garment type and so on), so the shop can show them as product cards. Empty for user messages. |
| `created_at` | TEXT | When the message was saved (UTC, set automatically). |

The 22 messages are 11 user/assistant pairs from 2 of the 3 users: 6 messages from the
test user and 16 from another user. Every assistant message has `products_json` and
no user message does. The sample conversation ("What hoodies do you have?",
"you have this in pink?") shows the chatbot answering catalogue questions about type,
price and color.

## Problem 4: Add user accounts

Accounts use the existing `users` table; there is no separate user system. A small
FastAPI backend (`backend/main.py`, port 8137) handles accounts, and the React
storefront calls it through Vite's `/api` proxy.

> **Later change (Problem 5):** the backend now runs from the `backend/` folder on port 8000 (`uvicorn main:app --reload --port 8000`), as the assignment requires, and the Vite proxy points there. The auth behaviour is unchanged.

### What is stored for a user

| Column | Stored value |
|---|---|
| `name` | First and last name together, e.g. "Hw4 Tester" (matches how seeded users are stored) |
| `first_name`, `last_name` | As entered at signup |
| `email` | Trimmed and lowercased; must be unique, and a login matches it case-insensitively |
| `password_hash` | `pbkdf2_sha256$<salt>$<digest>`. The plain-text password is never stored |
| `created_at` | Set automatically by the database |

### How passwords are protected

- **Hashing.** Each new account gets a random 16-hex-character salt
  (`secrets.token_hex(8)`). The password is run through **PBKDF2-HMAC-SHA256 with
  120,000 iterations**, and the 32-byte result is stored as hex.
- **Compatibility.** This is the same format the seeded accounts use. The iteration
  count isn't written in the stored hash, so it was confirmed by checking the seeded
  test account's known password against its existing hash, without changing it.
- **Why it's safe.** The salt makes identical passwords hash differently, and the
  120,000 iterations make guessing passwords from a stolen database slow.
- **Login checks.** Login re-computes the hash and compares it in constant time
  (`hmac.compare_digest`). A wrong password and an unknown email give the same error
  ("Incorrect email or password."), so attackers can't discover which emails have
  accounts.
- **Signup rules.** Passwords need at least 8 characters. The form also asks the user
  to confirm the password.
- **Nothing sensitive is exposed.** The API only ever returns `id`, `first_name`,
  `last_name`, `name` and `email`, never hashes or salts. Passwords and hashes are
  never logged; the server log shows only the request path and status.

### How login sessions work

- After signup or login, the backend sets a `cc_session` cookie containing
  `<user id>.<expiry>.<HMAC-SHA256 signature>`. The cookie is:
  - **HttpOnly**, so JavaScript can't read it;
  - **SameSite=Lax**;
  - valid for **7 days**.
- The signature uses a server secret: `SESSION_SECRET` from the environment, or else a
  random secret generated once into `backend/.session_secret`, which is excluded from
  git. An edited or forged cookie is rejected.
- On page load, the storefront calls `GET /api/auth/me`, which is how users stay
  logged in across refreshes. Logging out deletes the cookie.

### Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/auth/signup` | Create an account (first name, last name, email, password) and log in |
| `POST /api/auth/login` | Log in with email and password |
| `POST /api/auth/logout` | Log out |
| `GET /api/auth/me` | Return the logged-in user, or 401 |

### Testing

- **Seeded account.** The seeded test account (credentials supplied separately with the
  course materials; redacted here for the public repository) logs in, stays logged in
  and logs out. Its stored hash is unchanged, and all three
  seeded hashes are identical to the original download.
- **New account.** A new test account (`hw4.tester.<timestamp>@yale.edu`, user ID 4)
  was created through the API:
  - it signs up, stays logged in, logs out and logs back in;
  - it's stored as `pbkdf2_sha256` with a 16-character salt and a 64-character digest,
    with no plain-text password.
- **Rejected:** wrong passwords, unknown emails, duplicate emails (in any case), short
  passwords and forged cookies.
- **Storefront unaffected:** the full flow was also tested through the frontend's
  `/api` proxy. The storefront page, the 102-product catalogue, the images and all
  components still load.

## Problem 5: Build the chatbot backend

### How the front end talks to FastAPI

The React storefront (Vite dev server) sends every `/api/...` request to the FastAPI
app on `http://127.0.0.1:8000` through Vite's proxy (`frontend/vite.config.ts`).
Because the browser sees a single origin, the login cookie from Problem 4 works
without any CORS setup. The chat call is:

```
POST /api/chat   {"message": "...", "history": [{"role": "user"|"assistant", "content": "..."}, ...]}
→ 200 {"reply": "...Markdown...", "products": [{product_id, name, garment_type, image, price}, ...]}
```

`history` holds up to 20 earlier turns, oldest first, so follow-up questions have
context. The backend doesn't store conversations yet.

### Backend files

| File | Role |
|---|---|
| `backend/main.py` | The FastAPI app (run with Uvicorn): Problem 4 auth routes plus `POST /api/chat` |
| `backend/agent.py` | Agent entry and wiring: builds the PydanticAI `Agent` with the model, the prompt file, the tools and the output type |
| `backend/tools.py` | Tools the agent can call, plus a database helper for product cards |
| `backend/models.py` | Pydantic types: auth requests and responses, `ChatRequest`, `ChatTurn`, `ChatReply` (agent output), `ProductSummary` (tool result), `ProductCard`, `ChatResponse` |
| `backend/prompts/prompt.md` | The system prompt |
| `backend/auth.py` | Password hashing and session cookies (Problem 4) |

### How the agent is loaded

- **Model:** `gpt-5.6-luna` through the **Portkey** gateway, as a PydanticAI
  `OpenAIResponsesModel` on an `AsyncOpenAI` client with base URL
  `https://api.portkey.ai/v1`. This is configured in `backend/agent.py`
  (`MODEL_NAME`, overridable with the `MODEL_NAME` environment variable).
- **API key:** `PORTKEY_API_KEY` is read from `hw4/.env` or the shared `AI Class/.env`
  with `python-dotenv`. It's never in source code or logs. `.env` is git-ignored, and
  `.env.example` has placeholders only.
- **System prompt:** read from `backend/prompts/prompt.md` at start-up and passed as
  the agent's `instructions`; it isn't hard-coded in Python.
- **Agent:** `Agent(model, output_type=ChatReply, instructions=<prompt.md>,
  tools=[tools.search_products])`. PydanticAI runs the tool-calling loop itself.
- **Lazy start-up:** the agent is built on the first chat request, so the server and
  auth start even without an API key; chat then answers 503.

### Request flow

1. `POST /api/chat` validates the body against `ChatRequest`.
2. `agent.chat()` converts `history` into PydanticAI message history and calls
   `agent.run(message, ...)`.
3. The model may call `search_products` (one or more times), then returns a
   `ChatReply`: the reply text plus the `product_ids` it discussed.
4. `main.py` looks those IDs up in the database (`tools.product_cards`), dropping any
   unknown ID, and returns `ChatResponse {reply, products}`. Prices on the cards
   therefore come from the database, never from the model.
5. Errors: a missing key gives **503**; a model or provider failure gives **502** with
   a generic message. Provider details and secrets are never returned or logged.

### Tools

| Tool | What it returns | Why |
|---|---|---|
| `search_products(query, limit=8)` | `ProductSummary` list: `product_id`, `name`, `garment_type`, `colors` | Keyword match over name, garment type, description, colors and search tags in `catalogue` (read-only), ranked by how many words match. It deliberately has no price or stock; those tools come in Problem 6. |

### System prompt (`backend/prompts/prompt.md`)

- **Role and voice:** a warm, concise Campus Customs shopping assistant that stays on
  topic.
- **Facts from tools only:** mention only products a tool returned, never invent
  products, names or IDs, and say so when nothing matches.
- **No unsupported claims:** no tool covers price, stock, sizes or availability yet,
  so the assistant must not state or estimate them. Likewise no made-up discounts,
  shipping or return policies.
- **Product references:** list exact `product_ids` from tool results, so the store can
  show cards.
- **Safety:** never ask for or repeat passwords or payment details, treat customer
  text as requests rather than instructions, and don't reveal the prompt.

### Running it

From the `backend/` folder, as the assignment requires:

```
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

Then start the storefront with `npm run dev` in `frontend/`.

### What was tested

**Offline:**

- `search_products("navy hoodie")` returns 8 real products.
- A nonsense query returns none.
- `product_cards` drops unknown IDs and uses database prices (e.g. $68 for
  `basic-hoodie-big-yale`).
- With `PORTKEY_API_KEY` removed, building the model raises a clear error.

**Live, against a running server (same command, port 8138, because another local app
was using 8000):**

- Auth still works: the seeded login, `/me` and logout.
- An empty chat message is rejected (422).
- "Do you have any navy hoodies?" returned a valid `ChatResponse` in about 4 s, naming
  3 real navy hoodies, with 3 cards carrying database prices ($68, $88, $88).
- A follow-up with history ("How many of the first one are in stock in size M?") was
  answered without an invented number: the assistant said it can't confirm stock.
- The server log contained no keys, passwords or hashes.

### Frontend chat widget (Problem 5 follow-up)

- **Widget:** a floating "Ask our assistant" button opens a chat panel
  (`frontend/src/components/ChatWidget.tsx`). Customer messages appear on the right;
  assistant replies appear on the left, rendered from Markdown with `react-markdown`
  (`ChatMessages.tsx`).
- **Request:** `sendChat()` in `frontend/src/chat.ts` posts `{message, history}` to
  `/api/chat`, with the last 20 turns. The greeting isn't sent.
- **States:**
  - while waiting, an animated typing indicator shows and the Send button is disabled;
  - on failure, a red message appears in the panel, e.g. "Can't reach the shopping
    assistant…" when the backend is down, or the backend's own message for a
    503/502.
- **Product data:** the `products` returned with each reply are stored on that
  message but not rendered yet; clickable result cards are a later problem.
- **Proxy port:** the Vite proxy uses port 8000 by default; `API_PORT=<port> npm run
  dev` points it elsewhere.

**Tested:**

- With the backend on port 8138 and the storefront on `API_PORT=8138`, a live message
  ("Do you have any tennis gear?") went through the frontend proxy to `/api/chat`, and
  3 products came back.
- The widget's own `sendChat()` sent a live follow-up with history and got a correct
  answer (the tennis hoodie).
- `ChatMessages` rendered both user and assistant bubbles, with Markdown as HTML (no
  raw `**`), product data kept but no cards drawn, and the typing indicator while
  loading.
- With the backend stopped, `sendChat()` produced the "Can't reach the shopping
  assistant" message.
- The storefront page and catalogue still load.
- These tests ran in Node, calling the real widget code; the panel wasn't clicked in a
  real browser.

## Problem 6: Database tools

The agent now answers product, price and stock questions from `data/campus_customs.db`.
All three tools are in `backend/tools.py` and registered on the agent in
`backend/agent.py`: `tools=[search_products, get_product_details, check_inventory]`.

### The tools

| Tool | Reads | Returns | Use |
|---|---|---|---|
| `search_products(query, limit=8)` | `catalogue` | list of `ProductSummary` (since Problem 9: `SearchResults`, see below) | Find products from the customer's words, ranked by how many words match name, garment type, description, colors and search tags |
| `get_product_details(product_id)` | `catalogue` (one row) | `ProductDetails`, or `NotFound` | The authoritative **price** (plus description, colors, garment type) for one product |
| `check_inventory(product_id, size=None)` | `catalogue` + `inventory` | `InventoryResult`, or `NotFound` | The exact **quantity in stock** for one size, or for all sizes when no size is given |

**Read-only:** every tool opens SQLite with `file:...campus_customs.db?mode=ro`, so a
write fails with "attempt to write a readonly database". The tools only run `SELECT`
statements, and there is no tool that changes data.

### Lookup-result fields (`backend/models.py`) and why

| Model | Fields | Why these fields |
|---|---|---|
| `ProductSummary` | `product_id`, `name`, `garment_type`, `colors` | Enough to tell products apart and pick one. `product_id` is what the other tools and the product cards need. No price or stock here, so the model fetches those from the authoritative tools. |
| `ProductDetails` | `product_id`, `name`, `garment_type`, `description`, `colors`, `price` | Answers "how much / what is it like" for one product. `price` is the database value, unrounded. |
| `InventoryResult` | `product_id`, `name`, `sizes: list[SizeStock]` | Echoes which product was checked, so the reply names it correctly, and holds one or all sizes. |
| `SizeStock` | `size`, `quantity`, `in_stock` | `size` and `quantity` are copied straight from `inventory`. `in_stock` (`quantity > 0`) makes "out of stock" explicit, so 0 can't be misread. |
| `NotFound` | `error`, `valid_sizes` | Returned instead of data for an unknown product ID or a size that doesn't exist. `valid_sizes` (read from `inventory`) lets the assistant offer real alternatives instead of guessing. |

Sizes are matched against the `inventory` rows for that product, not a hard-coded list.
Common spellings are mapped first ("medium" → M, "2XL" → XXL).

### Prompt changes (`backend/prompts/prompt.md`)

- **Prices:** only from `get_product_details`, quoted exactly.
- **Stock, sizes and availability:** only from `check_inventory`, called again on every
  question rather than reusing an earlier answer. A quantity of 0 is stated as **out of
  stock**.
- **Workflow:** search first (or use the product_id from earlier in the
  conversation), then look up details or stock by exact `product_id`.
- **Uncertainty:** ask when several products match; report `NotFound` errors plainly
  with the valid sizes; say so when the database doesn't hold the information (e.g.
  shipping).

### Example: a price and stock question

> Customer: "How much is the Champion Reverse Weave Hoodie 1? And do you have it in size S and in XL? How many?"

1. The widget posts the message to `POST /api/chat`, and `agent.chat()` runs the
   PydanticAI agent.
2. The agent's tool calls, in order:
   - `search_products("Champion Reverse Weave Hoodie 1")` → ID
     `champion-reverse-weave-hoodie-1`;
   - `get_product_details("champion-reverse-weave-hoodie-1")` → `price: 68.0`;
   - `check_inventory(…, "S")` → `quantity: 25, in_stock: true`;
   - `check_inventory(…, "XL")` → `quantity: 0, in_stock: false`.
3. The reply: "The **Champion Reverse Weave Hoodie 1** is **$68.00**. Size S: 25 in
   stock. Size XL: Out of stock (0 available)." This matches the database exactly, and
   the backend attaches the product card with the database price.

### Tests

**Direct tool tests against the database (10/10 passed):**

- the real product is found;
- the exact price ($68.00) matches the database;
- size S returns 25, the exact quantity;
- size XL (0 in stock) is reported out of stock;
- with no size, all 6 sizes match the database;
- "medium"-style size words map to the right size;
- an invalid product returns `NotFound`;
- an invalid size (XXXL) returns `NotFound` with the real valid sizes;
- the tools' database connection refuses an `UPDATE`.

**Live through the PydanticAI agent (`gpt-5.6-luna` via Portkey):**

- The question above called `get_product_details` and `check_inventory`, and every
  number in the reply matched the database.
- "Yale Unicorn Cape" was reported as not found, with no invented price.
- The XXXL question went through `check_inventory`, which said XXXL isn't offered and
  listed XS–XXL.

**Through `POST /api/chat` with widget-style history:**

- "Do you have any Yale dad sweatshirts?" was followed by "How much is the hoodie one,
  and how many are left in medium?".
- The reply was "$68.00, 12 left in size M"; the database says $68.00 and 12.
- Product-card prices matched the database.
- Auth (login, `/me`, logout) still works.

**No changes or leaks:** the database file's SHA-256 was identical before and after
all of the tests, and the server log contained no keys or hashes.

## Problem 7: Dynamic product cards

Products that the chatbot finds now appear as clickable product cards under the
assistant reply that found them.

### How a search becomes cards

```
customer message ─► POST /api/chat ─► PydanticAI agent ─► search_products / get_product_details (SQLite, read-only)
                                            │
                                            ▼
                         ChatReply {reply, product_ids}   (the IDs the model referenced, copied from tool results)
                                            │
             main.py: tools.product_cards(product_ids) ─► SELECT name, image_file_path, price FROM catalogue
                                            │            (unknown IDs dropped, so the model can't invent a card)
                                            ▼
                    ChatResponse {reply, products: [ProductCard{product_id, name, garment_type, image, price}]}
                                            │
     React: the widget stores products on THAT assistant message ─► ChatMessages renders <ProductCard compact/> per product
```

- **Card data comes from the database.** The model only chooses *which* product IDs
  are relevant. Each card's name, image path and price come from the `catalogue` row,
  so a card can't show an invented product or price.
- **Cards are dynamic.** The frontend has no list of products for particular phrases;
  it renders whatever `products` the response contains. A check of `frontend/src`
  found no product IDs anywhere in it.
- **Each reply keeps its own cards.** Products are saved on the specific assistant
  message they came with, and each message renders only its own `products`. A later
  reply can't overwrite or re-attach an earlier reply's cards.

### Reused components and the single-item view

- Chat results use the same `ProductCard` component as the storefront grid, with a
  `compact` layout for the narrow chat panel. The card takes the fields both sources
  provide (`product_id`, `name`, `image`, `price`).
- Every card links to `productHref(product_id)` = `#/product/<product_id>`, the same
  link the storefront uses. Clicking a chat card opens the existing `ProductView` from
  Problem 3 (`App.tsx` reads the hash); there's no separate chatbot product page. The
  chat panel stays open over the page.

### Tests (live `gpt-5.6-luna` via Portkey, run through the real chat code)

- **Two different searches:**
  - "Show me navy hoodies." → `basic-hoodie-big-yale`,
    `brooks-brothers-double-knit-full-zip-hoodie-yale`, `champion-full-zip-hood`, all
    hoodies;
  - then, with history, "Do you have anything for tennis players?" →
    `squash-left-chest-tennis`, `tri-blend-sports-tennis-t-shirt`,
    `yale-sports-hoodie-tennis`, all tennis products.

  The two sets differ.
- **Rendering:** with the real `ChatMessages`, message 1 showed exactly the
  first set and message 3 exactly the second; user messages showed no cards.
- **Every card matches the database:** each card's name, image (`/products/<id>.jpg`)
  and price matched the `catalogue` row (e.g. Basic Hoodie Big Yale $68.00, Tri Blend
  Sports Tennis T Shirt $32.00, Yale Sports Hoodie Tennis $45.00), and every product
  exists in the storefront catalogue.
- **Same single-item view:** a chat card and the storefront card for the same product
  have the identical link (`#/product/basic-hoodie-big-yale`), and that product renders
  in the existing `ProductView`.
- **Storefront unchanged:** the page and the 102-product catalogue load, and the grid
  still uses the full-size card.
- **Not run in a browser:** these tests used the real components and the live API in
  Node. The cards weren't clicked in a real browser.

## Problem 8: Customer context and persistent chat history

### How authenticated identity is established

- The backend identifies the customer **only** from the signed, HttpOnly `cc_session`
  cookie (Problem 4), through `_current_user()` in `backend/main.py`. Nothing in the
  request body can choose which user a message belongs to.
- For a logged-in customer, the agent receives a `ChatContext` (PydanticAI `deps`)
  containing `logged_in=True` and the customer's **first name** only. No email,
  password hash, cookie or secret is ever given to the model.
- A dynamic instruction (`@agent.instructions` in `backend/agent.py`) turns that
  context into a short "Current customer context" section of the system prompt.

### How chat messages are saved and loaded (existing `chat_messages` table)

- **Saving** (`POST /api/chat`, logged in): after a successful reply, the backend
  inserts two rows under the authenticated user's id, in one transaction:
  - the customer's message: `role='user'`, `products_json` NULL;
  - the reply: `role='assistant'`, with `products_json` holding one snapshot per
    referenced product.

  The snapshot uses the same keys as the existing rows: `product_id`, `name`,
  `garment_type`, `description`, `colors`, `search_tags`, `image_file_path`,
  `image_url`, `price`, `inventory`, `total_stock`. If the model call fails, nothing
  is saved.
- **Agent context:** for a logged-in customer, the conversation history given to the
  agent is loaded from `chat_messages` (the last 20 rows for that `user_id`), not
  taken from the browser.
- **Loading** (`GET /api/chat/history`): returns the logged-in user's own messages in
  order. Product cards are rebuilt from the `product_id`s in `products_json`, looked
  up in the current catalogue, so restored cards show today's real name, image and
  price. This works for the seeded rows too.
- **Frontend** (`ChatWidget.tsx`):
  - when a user logs in, or the page reloads while logged in, the widget calls
    `fetchHistory()` and shows the saved conversation with its cards;
  - on logout, it clears the panel;
  - the panel header shows "Chatting as <first name> · history saved" or "Guest chat
    · not saved".

### How guests differ

Guests can chat normally. Their history lives only in the open widget and is sent with
each request for context during that visit. **Nothing is written to `chat_messages`**,
the response says `saved: false`, and `GET /api/chat/history` returns 401.

### How current-page context reaches the agent

- The widget reads the current page from the URL hash (`#/product/<product_id>`) and
  sends it as `current_product_id` with each message.
- The backend **doesn't trust it.** `tools.validate_product()` looks the exact ID up in
  `catalogue`; an unknown ID is ignored, so the agent gets no product context.
- A valid product's ID and name go into `ChatContext.current_product`, and the prompt
  tells the agent that "this / it / this one" means that product. The agent is still
  told to fetch price, description and stock with the Problem 6 tools using that
  `product_id`: the page context only says *which* product, never its facts.
- The response echoes the validated `current_product_id`, or null.

### How user histories stay isolated

Every read and write of `chat_messages` is filtered by the user id from the session
cookie: `WHERE user_id = ?`. There's no endpoint that accepts a user id from the
browser. On logout, the widget clears its messages, so the next person at the same
browser doesn't see the previous conversation.

### Tests (live `gpt-5.6-luna` via Portkey, through the frontend's `/api` proxy)

The tests used test accounts made for this homework: user 4, and user 5 created
during the tests. They didn't use the seeded users' conversations.

- **Guest:** chatted and got product cards; no `chat_messages` rows were created; the
  history endpoint returned 401.
- **Saving:** user 4 asked "Show me navy crewneck sweatshirts.", which returned
  `saved: true` and added exactly 2 rows (user message, then assistant reply). The
  `products_json` used the same 11 keys as the existing rows.
- **Reload:** a fresh session for user 4 restored the history, including that exchange.
  The restored cards were the same products, with database prices.
- **Isolation:**
  - new user 5 started with an empty history, then saw only their own 2 messages;
  - user 4 saw none of user 5's messages;
  - the seeded test user saw exactly their own 6 seeded messages, with cards rebuilt
    from the seeded `products_json`.
- **Context, price:** "How much is this?" on `champion-reverse-weave-hoodie-1`
  returned **$68.00**, the database price, and the response echoed the product ID.
- **Context, stock:** "Do you have this in medium?" on the same page made the agent
  call `check_inventory(product_id='champion-reverse-weave-hoodie-1', size='M')`, and
  it answered **20**, the database value.
- **Invalid page product:** `current_product_id = "fake-product-123"` was ignored
  (echoed as null). The agent asked which product was meant and gave no price.
- **Widget code:** the real `fetchHistory()` loaded user 4's saved messages with cards,
  and `sendChat()` sent the page product as context (`yale-dad-hoodie`). The reply was
  saved.
- **Nothing else changed:** auth, searches and dynamic cards still work. The 22 seeded
  `chat_messages` rows were byte-for-byte unchanged before and after. The server log
  contained no keys, passwords or hashes.

## Problem 9: Usability improvements

Four improvements are described in full in `output/usability.md`. The changes to the
system described above:

- **Tools.** The agent now has four read-only tools: `search_products`,
  `resolve_product`, `get_product_details` and `check_inventory` (`backend/agent.py`).
  - `search_products` returns `SearchResults` with `matches`, `ignored_words` and
    `suggestions` (real garment types when nothing matches). Words found in more than
    half of all products (e.g. "yale") can't create a match on their own when the
    query has more specific words.
  - `resolve_product(reference)` returns a `ProductResolution` (`unique` /
    `ambiguous` with candidates / `not_found`) from the `catalogue` table.
- **Prompt.** New rules: report no-match searches honestly with real suggestions;
  resolve named products before price or stock lookups; ask the customer to choose
  when a reference is ambiguous.
- **Chat API.**
  - `ChatRequest.history_after_id`: a logged-in "New chat" boundary. Only saved
    messages after it are used as agent context; nothing is deleted.
  - `ChatResponse.last_message_id`: the saved reply's id.
  - `GET /api/chat/history` now includes each message's `id`.
- **Frontend.** A **New chat** button in the chat panel (the boundary is kept per tab
  in `sessionStorage`, with "Show earlier messages" to undo it), and a no-results
  state with Clear search and category suggestions (`NoResults.tsx`).
- **Dev dependency.** `jsdom` (frontend dev-only) is used to test the full app in a
  simulated browser.

**Problem 9 regression checks.** The existing behaviours were re-verified live after the
changes:

- authentication (login);
- persistent history (saved exchanges, history loading after login);
- current-product context ("How much is this?" on `champion-reverse-weave-hoodie-1` →
  $68.00);
- dynamic product cards in chat;
- normal chat search (tennis → 3 tennis products) and storefront search ("hoodie" → 27
  of 102);
- guests still save nothing;
- the 22 seeded `chat_messages` rows are byte-for-byte unchanged.

## Problem 10: Storefront styling

The frontend has a Yale-inspired visual design. The details are in
`output/design.md`. No behaviour, API, data or product information changed.

- **New decorative components:**
  - `HandsomeDan.tsx`: an original SVG bulldog in a Yale sweater, used in the hero,
    the header badge and the chat header;
  - `CampusBorders.tsx` with `public/decor/campus-border.svg`: original campus line art
    for the side frames, shown at 1400 px wide or more;
  - `PawTrail.tsx`: the mouse paw-print trail. It's off for
    `prefers-reduced-motion` and on touch devices.

  All are `aria-hidden` and `pointer-events: none`.
- **Theme layer:** `index.css` remaps the palette to Yale blue, light blue, white and
  cream, and uses system serif, sans and handwritten font stacks (no font files).
- **Layering fix:** the sticky header has `z-index: 20`, so the login dialog inside it
  stays above the page content. Browser testing caught this regression during
  development.
- **Dev dependency:** `playwright-core` (frontend dev-only) drives the locally
  installed Google Chrome for browser tests; no browser is downloaded.

