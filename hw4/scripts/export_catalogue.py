"""Export the Campus Customs catalogue from data/campus_customs.db for the storefront.

Reads the `catalogue` table (read-only) and writes frontend/public/catalogue.json,
keeping every product_id exactly as stored. Copies each product's photo from
data/products/ into frontend/public/products/ so the storefront serves the real images.

Run automatically by `npm run dev` / `npm run build` (see frontend/package.json).
"""

import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "campus_customs.db"
PUBLIC = ROOT / "frontend" / "public"


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT product_id, name, garment_type, description, colors, search_tags, image_file_path, price "
        "FROM catalogue ORDER BY name"
    ).fetchall()
    con.close()

    (PUBLIC / "products").mkdir(parents=True, exist_ok=True)
    products = []
    for r in rows:
        src = ROOT / "data" / r["image_file_path"]  # e.g. products/basic-hoodie-big-yale.jpg
        if not src.exists():
            raise FileNotFoundError(f"missing image for {r['product_id']}: {src}")
        shutil.copy2(src, PUBLIC / r["image_file_path"])
        products.append(
            {
                "product_id": r["product_id"],
                "name": r["name"],
                "garment_type": r["garment_type"],
                "description": r["description"],
                "colors": json.loads(r["colors"]),
                "search_tags": json.loads(r["search_tags"]),
                "image": "/" + r["image_file_path"],
                "price": r["price"],
            }
        )
    (PUBLIC / "catalogue.json").write_text(json.dumps(products, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(products)} products and images to {PUBLIC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
