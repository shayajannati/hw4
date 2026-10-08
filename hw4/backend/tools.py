"""Tools the Campus Customs agent can call. Every fact comes from data/campus_customs.db.

All tools open the database read-only (SQLite `mode=ro`), so the agent can never change
catalogue or inventory data.

    search_products(query)                 -> find products by keywords, or grounded suggestions (catalogue)
    resolve_product(reference)             -> is "the X" one product, several, or none? (catalogue)
    get_product_details(product_id)        -> price, description, colors (catalogue)
    check_inventory(product_id, size=None) -> stock for one size or all sizes (inventory)
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from models import (
    CurrentProduct,
    InventoryResult,
    NotFound,
    ProductCard,
    ProductDetails,
    ProductResolution,
    ProductSummary,
    SearchResults,
    SizeStock,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
MAX_RESULTS = 12
COMMON_WORD_SHARE = 0.5  # words found in more than half of all products (e.g. "yale") don't help matching
STOP_WORDS = {"the", "a", "an", "and", "or", "for", "of", "in", "on", "with", "do", "you", "have", "any", "some",
              "is", "it", "me", "show", "i", "want", "need", "looking", "find", "what", "your", "my", "this", "that",
              "one", "ones", "item", "items", "thing", "things", "product", "products", "merchandise", "merch", "stuff"}
SIZE_ALIASES = {
    "extra small": "XS", "xsmall": "XS", "small": "S", "medium": "M", "med": "M", "large": "L",
    "extra large": "XL", "xlarge": "XL", "2xl": "XXL", "xxlarge": "XXL", "2x": "XXL", "double xl": "XXL",
}


def _read_only() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _catalogue_rows(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return con.execute(
        "SELECT product_id, name, garment_type, description, colors, search_tags FROM catalogue ORDER BY name"
    ).fetchall()


def _searchable(r: sqlite3.Row) -> str:
    return " ".join([r["name"], r["garment_type"], r["description"], r["colors"], r["search_tags"]]).lower()


def _summary(r: sqlite3.Row) -> ProductSummary:
    return ProductSummary(product_id=r["product_id"], name=r["name"], garment_type=r["garment_type"], colors=json.loads(r["colors"]))


def _query_words(text: str, rows: list[sqlite3.Row]) -> tuple[list[str], list[str]]:
    """(all useful words, the common ones). Common = found in more than half of all products (e.g. "yale")."""
    words = [w for w in dict.fromkeys(re.findall(r"[a-z0-9]+", text.lower())) if len(w) > 1 and w not in STOP_WORDS]
    texts = [_searchable(r) for r in rows]
    common = [w for w in words if sum(w in t for t in texts) > COMMON_WORD_SHARE * len(texts)]
    return words, common


def search_products(query: str, limit: int = 8) -> SearchResults:
    """Search the Campus Customs catalogue by keywords.

    Matches words in the product name, garment type, description, colors and search
    tags (e.g. "navy hoodie", "Berkeley", "dad", "tennis"). Products matching more of
    the words come first. Words that most products share (like "yale" or "navy") help
    ranking but can't make a match on their own when the query has more specific words.
    If nothing matches, `matches` is empty and `suggestions` lists real garment types
    the store carries, so you can suggest a broader search.

    Args:
        query: The customer's key words.
        limit: Maximum number of products to return (1-12).
    """
    with _read_only() as con:
        rows = _catalogue_rows(con)
    words, common = _query_words(query, rows)
    specific = [w for w in words if w not in common]
    scored = []
    for r in rows:
        text = _searchable(r)
        if specific and not any(w in text for w in specific):
            continue  # e.g. "yale unicorn cape": matching only "yale" isn't a real match
        score = sum(1 for w in words if w in text)
        if score:
            scored.append((score, r["name"], r))
    scored.sort(key=lambda t: (-t[0], t[1]))
    limit = max(1, min(limit, MAX_RESULTS))
    matches = [_summary(r) for _, _, r in scored[:limit]]
    suggestions = []
    if not matches:  # grounded fallback: real categories from the catalogue, most common first
        counts: dict[str, int] = {}
        for r in rows:
            counts[r["garment_type"].lower()] = counts.get(r["garment_type"].lower(), 0) + 1
        suggestions = [g for g, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:8]]
    return SearchResults(
        query=query, matches=matches, ignored_words=common if specific and not matches else [], suggestions=suggestions
    )


def resolve_product(reference: str) -> ProductResolution:
    """Work out which ONE product the customer means before a price, description or stock lookup.

    Use this when the customer names or describes a product (e.g. "the dad hoodie",
    "the tennis shirt", "Basic Hoodie Big Yale"). Returns status:
    - "unique": exactly one product fits -> use `product.product_id` with the other tools;
    - "ambiguous": several real products fit -> list `candidates` and ask which one; don't pick;
    - "not_found": nothing fits -> say so and offer a search.

    Args:
        reference: The customer's words for the product.
    """
    with _read_only() as con:
        rows = _catalogue_rows(con)
    ref = reference.strip().lower()
    exact = [r for r in rows if ref in (r["product_id"].lower(), r["name"].lower())]
    if len(exact) == 1:
        return ProductResolution(status="unique", product=_summary(exact[0]))
    words, _ = _query_words(reference, rows)
    if not words:
        return ProductResolution(status="not_found")
    # A product fits when every useful word appears in its name, garment type or colors/tags.
    fits = [r for r in rows if all(w in _searchable(r) for w in words)]
    # Prefer products whose NAME contains every word (e.g. "dad hoodie" -> Yale Dad Hoodie).
    in_name = [r for r in fits if all(w in (r["name"] + " " + r["garment_type"]).lower() for w in words)]
    best = in_name or fits
    if len(best) == 1:
        return ProductResolution(status="unique", product=_summary(best[0]))
    if not best:
        return ProductResolution(status="not_found")
    return ProductResolution(status="ambiguous", candidates=[_summary(r) for r in best[:MAX_RESULTS]])


def _find_product(con: sqlite3.Connection, product_id: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id.strip(),)).fetchone()


def get_product_details(product_id: str) -> ProductDetails | NotFound:
    """Get the authoritative price, description and colors for ONE product from the catalogue.

    Always use this for price questions; never state a price from memory.

    Args:
        product_id: The exact product_id from search_products (e.g. "basic-hoodie-big-yale").
    """
    with _read_only() as con:
        row = _find_product(con, product_id)
    if row is None:
        return NotFound(error=f"No product with product_id {product_id!r}. Use search_products to find the right ID.")
    return ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
    )


def _normalize_size(size: str) -> str:
    s = " ".join(size.strip().lower().replace("-", " ").split())
    return SIZE_ALIASES.get(s, SIZE_ALIASES.get(s.replace(" ", ""), size.strip().upper()))


def check_inventory(product_id: str, size: str | None = None) -> InventoryResult | NotFound:
    """Check how many units of ONE product are in stock, from the inventory table.

    Always use this for stock, size or availability questions; never guess. A quantity
    of 0 means that size is out of stock.

    Args:
        product_id: The exact product_id from search_products.
        size: One size such as "M", "medium", "XL" or "2XL". Leave empty to get every size.
    """
    with _read_only() as con:
        product = _find_product(con, product_id)
        if product is None:
            return NotFound(error=f"No product with product_id {product_id!r}. Use search_products to find the right ID.")
        rows = con.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product["product_id"],)
        ).fetchall()
    order = {s: i for i, s in enumerate(["XS", "S", "M", "L", "XL", "XXL"])}  # display order only
    rows = sorted(rows, key=lambda r: order.get(r["size"], 99))
    if size is not None and size.strip():
        wanted = _normalize_size(size)
        rows_for_size = [r for r in rows if r["size"].upper() == wanted]
        if not rows_for_size:
            return NotFound(
                error=f"{product['name']} has no size {size!r} in inventory.",
                valid_sizes=[r["size"] for r in rows],
            )
        rows = rows_for_size
    return InventoryResult(
        product_id=product["product_id"],
        name=product["name"],
        sizes=[SizeStock(size=r["size"], quantity=r["quantity"], in_stock=r["quantity"] > 0) for r in rows],
    )


def product_cards(product_ids: list[str]) -> list[ProductCard]:
    """Database rows for the products the agent referenced (unknown IDs are dropped)."""
    ids = list(dict.fromkeys(product_ids))  # unique, order kept
    if not ids:
        return []
    with _read_only() as con:
        rows = {
            r["product_id"]: r
            for r in con.execute(
                f"SELECT product_id, name, garment_type, image_file_path, price FROM catalogue "
                f"WHERE product_id IN ({','.join('?' * len(ids))})",
                ids,
            )
        }
    return [
        ProductCard(
            product_id=pid,
            name=rows[pid]["name"],
            garment_type=rows[pid]["garment_type"],
            image="/" + rows[pid]["image_file_path"],
            price=rows[pid]["price"],
        )
        for pid in ids
        if pid in rows
    ]


# --- Helpers for customer context & saved history (not agent tools) ------------


def validate_product(product_id: str | None) -> CurrentProduct | None:
    """The catalogue product with this exact ID, or None. Never trust a browser-supplied ID without this."""
    if not product_id or not product_id.strip():
        return None
    with _read_only() as con:
        row = _find_product(con, product_id)
    return CurrentProduct(product_id=row["product_id"], name=row["name"]) if row else None


def product_snapshots(product_ids: list[str]) -> list[dict]:
    """products_json entries in the same shape as the existing chat_messages rows."""
    ids = list(dict.fromkeys(product_ids))
    out = []
    with _read_only() as con:
        for pid in ids:
            row = _find_product(con, pid)
            if row is None:
                continue
            inventory = [
                {"size": r["size"], "quantity": r["quantity"]}
                for r in con.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (pid,))
            ]
            out.append(
                {
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "garment_type": row["garment_type"],
                    "description": row["description"],
                    "colors": json.loads(row["colors"]),
                    "search_tags": json.loads(row["search_tags"]),
                    "image_file_path": row["image_file_path"],
                    "image_url": "/" + row["image_file_path"],
                    "price": row["price"],
                    "inventory": inventory,
                    "total_stock": sum(i["quantity"] for i in inventory),
                }
            )
    return out
