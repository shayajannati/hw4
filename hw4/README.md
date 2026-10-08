# Campus Customs: AI storefront (MGT 409, Homework 4)

A Yale-themed online store for **Campus Customs** merchandise, with an AI shopping
assistant. Customers browse and search 102 real products, open product pages, create
an account, and chat with an assistant that looks up **real prices and stock** from
the store's database. Chat results appear as clickable product cards.

## Features

- **Storefront:** a product grid, search (with a helpful no-results state), and
  single-product pages. React + Vite + TypeScript, styled with Yale blue and cream, an
  original bulldog mascot, campus line-art borders and a paw-print cursor trail.
- **Accounts:** signup, login and logout using the existing `users` table. Passwords
  are stored as salted PBKDF2-SHA256 hashes, and logins use a signed HttpOnly session
  cookie.
- **Shopping assistant:**
  - a PydanticAI agent using `gpt-5.6-luna` through Portkey, with four **read-only**
    database tools (`search_products`, `resolve_product`, `get_product_details`,
    `check_inventory`);
  - prices and stock always come from the database, and ambiguous requests get a
    clarifying question;
  - unknown items get an honest "not found" answer.
- **Product cards in chat:** clicking one opens the same product page as the
  storefront.
- **Customer context:**
  - logged-in customers' chats are saved and restored (each customer sees only their
    own);
  - guests can chat without anything being saved;
  - "How much is *this*?" on a product page refers to that product.
- **Safety and auditing:**
  - explicit safety rules in `backend/prompts/prompt.md`;
  - PydanticAI usage limits (8 model requests and 12 tool calls per message);
  - an append-only audit trail in `output/audit_trail.json`, with secrets redacted.

## Tech stack

| Part | Technology |
|---|---|
| Frontend | React 19, Vite, TypeScript, `react-markdown` |
| Backend | Python, FastAPI, Uvicorn |
| Agent | PydanticAI (`pydantic-ai-slim[openai]`): `Agent`, tools, structured output, `UsageLimits` |
| Model | `gpt-5.6-luna` via the [Portkey](https://portkey.ai) gateway |
| Data | SQLite `data/campus_customs.db` (course-provided, **not** in this repo) |

## Prerequisites

- Python 3.12+ (tested on 3.14) and Node.js 20+ (tested on 24)
- A Portkey API key (only needed for the chatbot)
- The course **data pack**, placed locally (see below)

## 0. Get the code

The project lives in the `hw4/` folder of this repository, so every command below is run
from inside it:

```bash
git clone https://github.com/shayajannati/hw4.git
cd hw4/hw4
```

## 1. Place the course data pack (not in git)

The course database and product photos are intentionally **excluded from this public
repository** (`.gitignore`). Copy the course-provided `data/` folder into the `hw4/`
folder (next to `backend/` and `frontend/`) so it looks like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/        # the 102 product images referenced by the catalogue
```

The storefront's catalogue (`frontend/public/catalogue.json`) and image copies
(`frontend/public/products/`) are generated from this data automatically when the
frontend starts. Without the data pack the frontend won't start, and the backend's
login and chat can't work.

## 2. Install

From the `hw4/` folder:

```bash
cp .env.example .env              # then put your Portkey key in .env
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd frontend && npm ci && cd ..
```

**Environment variables** (see `.env.example`):

- `PORTKEY_API_KEY` is required for chat.
- Optional: `PORTKEY_BASE_URL`, `MODEL_NAME` (default `gpt-5.6-luna`),
  `SESSION_SECRET` (otherwise generated into the git-ignored
  `backend/.session_secret`), `AUDIT_TRAIL_PATH`.
- Never commit your real `.env`.

## 3. Run (two terminals)

**Backend** (run from the `backend/` folder), on **http://127.0.0.1:8000**:

```bash
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

**Frontend**, on **http://localhost:5173**:

```bash
cd frontend
npm run dev
```

Open the URL Vite prints. The frontend forwards all `/api/...` requests to the backend
on port 8000.

- **Port 8000 already in use?** Start uvicorn with `--port <other>` and the frontend
  with `API_PORT=<other> npm run dev`.
- **Try it:** sign up for an account, or log in with the course test account (test
  credentials are supplied separately with the course materials and aren't published
  here). Then click **💬 Ask our assistant** and try:
  - "Show me your hoodies";
  - "How many Yale Dad Hoodies do you have in size M?";
  - "How much is this?" on a product page.

## Project layout

```
hw4/
├── AI_prompts.md          # log of every prompt used to build the project
├── README.md
├── requirements.txt       # backend dependencies
├── .env.example           # environment variables (placeholders only)
├── .gitignore
├── backend/
│   ├── main.py            # FastAPI app: auth, /api/chat, /api/chat/history
│   ├── agent.py           # PydanticAI agent (model, prompt, tools, limits)
│   ├── tools.py           # read-only database tools
│   ├── models.py          # Pydantic / PydanticAI structured types
│   ├── prompts/prompt.md  # system prompt + safety rules
│   ├── auth.py            # password hashing, session cookies
│   └── audit.py           # append-only audit trail
├── frontend/              # Vite + React + TypeScript storefront
│   ├── src/               # app, components (ProductCard, ProductView, ChatWidget, …)
│   └── public/decor/      # original campus line-art border (Problem 10)
├── scripts/
│   └── export_catalogue.py  # builds the storefront catalogue from data/ (run automatically)
└── output/
    ├── harness.md         # full technical reference (models, tools, safety, limits, how to run)
    ├── usability.md       # the four Problem 9 usability improvements
    ├── design.md          # Problem 10 design choices
    ├── app_check.html     # Problem 11 browser test report (open in a browser)
    ├── app_check_images/  # screenshots used by app_check.html
    └── audit_trail.json   # append-only audit trail of chatbot activity
```

## Output artifacts

- **`output/harness.md`:** how the whole system works. It covers the model and
  Portkey setup, every tool and data model (and why its fields were chosen), the
  safety rules and where they're enforced, the execution limits and result caps,
  identity and history isolation, the audit trail, and verified setup and run
  commands.
- **`output/usability.md`:** two frontend and two agent/backend usability
  improvements, and how each was tested.
- **`output/design.md`:** the Yale-inspired visual design: palette, typography,
  mascot, campus borders, paw-print trail and accessibility.
- **`output/app_check.html`:** real-browser test evidence (inventory lookup, dynamic
  product cards, a usability feature, and regression checks). Images use relative
  paths into `output/app_check_images/`.
- **`output/audit_trail.json`:** an append-only record of each chat request: time,
  agent steps, tools with shortened arguments and results, stop reasons, and the
  outcome. API keys, password hashes, cookies and emails are never recorded.
