# Usability improvements (Problem 9)

Exactly four improvements: two frontend and two agent/backend. Each was checked
against Problems 3–8 before implementation (see "Was this already there?" in each
section).

## 1. Frontend Improvement 1: "New chat" control

**Usability problem.** The chat widget had no way to start over. A guest's panel kept
growing all visit. A logged-in customer always reopened to their entire saved history,
and that history was also fed to the assistant as context, so an old topic could
colour a new question. *Was this already there?* No: Problems 5–8 had no reset
control.

**What changed** (`frontend/src/components/ChatWidget.tsx`, `frontend/src/chat.ts`,
`backend/main.py`, `backend/models.py`):

- A **New chat** button in the chat panel header.
- **Guest:** clears the in-memory conversation back to the greeting (nothing was ever
  saved).
- **Logged in:** nothing is deleted.
  - The widget records a "new conversation" boundary: the id of the last saved message,
    kept in `sessionStorage` for that browser tab.
  - Messages up to the boundary are hidden. A notice says "New conversation started.
    Your N earlier messages are still saved to your account", with a **Show earlier
    messages** link that restores them.
  - The widget sends `history_after_id` with each message. The backend then only uses
    saved messages after the boundary as the assistant's context, so the new
    conversation really starts fresh.
  - New messages are still saved to `chat_messages` as before.

**Why it helps.** Customers can switch topics cleanly, guests can tidy the panel, and
logged-in customers never lose saved history by accident.

**How it was tested.** The whole React app was rendered in a simulated browser
(`jsdom`) against the live backend, with clicks on the real buttons:

- **Guest:** after a real chat, New chat left only the greeting, and no
  `chat_messages` rows were written.
- **Logged in:**
  - all 6 saved messages loaded;
  - New chat showed a fresh panel plus the "still saved" notice, with **0 rows
    deleted**;
  - the next message sent `history_after_id` equal to the last saved id (30), and the
    new exchange was saved (+2 rows);
  - after a remount (reload), only the 2 new messages showed;
  - **Show earlier messages** restored all 8.

## 2. Frontend Improvement 2: Clear no-results state for storefront search

**Usability problem.** A search with no matches showed only a short grey line ("No
products match your search."). It didn't repeat what was searched, suggest anything,
or offer a way back. Customers had to notice the search box and erase it by hand.
*Was this already there?* Only that bare line, from Problem 3; there was no
explanation, reset control or suggestions.

**What changed** (`frontend/src/components/NoResults.tsx`, `frontend/src/App.tsx`,
`frontend/src/index.css`):

- A clear empty state: "No products match "<query>"", with tips (shorter word, check
  spelling).
- A **Clear search & show all 102 products** button.
- **Popular categories** links, computed from the real catalogue (its most common
  garment types), so nothing is hard-coded.
- A **Clear** button beside the search box whenever it has text.

**Why it helps.** Customers understand why they see nothing and get back to the full
catalogue, or to a sensible category, in one click instead of a dead end.

**How it was tested** (same full-app simulated browser, with real typing and clicks):

- searching "xyzzy plaid kilt" showed the new message naming the query, with no cards;
- **Clear search & show all** restored all 102 products and emptied the box;
- clicking the suggested category "crewneck sweatshirt" ran that search (27 products);
- the Clear button beside the box reset the grid;
- a normal search ("hoodie" → 27 of 102) still worked.

## 3. Agent/Backend Improvement 1: Helpful product-search fallback

**Usability problem.** For an item the store doesn't carry, the search tool still
returned loosely related "matches", because words like "yale" (or "merchandise")
appear in almost every product. That invited the assistant to present unrelated
products, or to give a bare "can't find it" with nowhere to go. *Was this already
there?* The Problem 5 prompt had one line ("if nothing matches, say so"), but the
tool itself never reported "no matches" for these queries and offered nothing
grounded to suggest.

**What changed** (`backend/tools.py`, `backend/models.py`,
`backend/prompts/prompt.md`):

- `search_products` now returns `SearchResults`:
  - `matches` (as before);
  - `ignored_words`;
  - `suggestions` when nothing matches: the store's real garment types, read from the
    `catalogue` table.
- Filler words ("any", "merchandise", "one"…) are skipped.
- Words found in more than half of all products, like "yale" or "navy", still help
  ranking, but can't create a match on their own when the query has more specific
  words. So "Yale unicorn cape" now correctly returns no matches, while "navy hoodie"
  still ranks navy hoodies first.
- The prompt says: if there are no matches, say so clearly, don't offer products that
  weren't returned, and suggest a broader search using the real `suggestions` or ask
  what the customer wants.

**Why it helps.** Customers get an honest answer plus a useful next step, and never a
made-up or irrelevant product.

**How it was tested** (live `gpt-5.6-luna` via Portkey, real tools and database):

- "Do you sell a Yale unicorn cape?" made the agent call `search_products`, which
  returned **0 matches**.
- The reply: "I couldn't find a Yale unicorn cape at Campus Customs. We do carry items
  such as hoodies, crewneck sweatshirts, T-shirts, quarter-zips, and fleece jackets.
  Would you like to search one of those categories?"
- It had no product cards and no prices, and the suggested categories are real
  catalogue garment types.

## 4. Agent/Backend Improvement 2: Clarifying ambiguous product references

**Usability problem.** Customers often say things like "the dad one" or "the tennis
shirt", which fit several real products. The agent could silently pick one and quote
its price or stock, giving the customer facts about the wrong item. *Was this already
there?* The Problem 6 prompt had one sentence ("if several products could match…
ask"), but there was no mechanism to detect ambiguity, so it depended on the model
noticing.

**What changed** (`backend/tools.py`, `backend/models.py`, `backend/agent.py`,
`backend/prompts/prompt.md`):

- A new read-only tool, `resolve_product(reference)`, returns a `ProductResolution`
  with status `unique`, `ambiguous` (with the real `candidates`) or `not_found`. It
  decides deterministically from the `catalogue` table, and the tool is registered on
  the agent.
- The prompt now says:
  - call `resolve_product` before a price, description or stock lookup on a named
    product;
  - if the result is ambiguous, don't pick and don't look anything up: list the real
    candidates as product cards and ask which one;
  - in the next message, match the customer's answer ("the hoodie") to those
    candidates from the conversation history, then look it up.

**Why it helps.** Customers get the price or stock of the product they actually mean,
can choose from clickable cards, and can answer naturally in a follow-up.

**How it was tested** (live, real agent, tools and database):

- **Agent:** "How much is the dad one?" made the agent call
  `resolve_product('the dad one')`, which returned **ambiguous**:
  `yale-dad-crewneck`, `yale-dad-hoodie`, `yale-dad-t-shirt`. It called **no** price
  tool. The reply asked "Which "Dad" item do you mean?" and listed those three as
  cards.
- **Endpoint with saved history:** a logged-in user asked "How much is the dad one?",
  which gave the same clarifying question with 3 cards. The follow-up "The hoodie,
  please." returned "The **Yale Dad Hoodie** is **$68.00**", which matches the
  database, with its card. That exchange was saved to history.
