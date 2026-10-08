from __future__ import annotations

import json
import sqlite3
from functools import lru_cache
from pathlib import Path

try:
    from .audit import audit_event
    from .models import ProductCard, ProductInfo, StockLine, StockResult
except ImportError:  # Supports imports when launched from backend/.
    from audit import audit_event
    from models import ProductCard, ProductInfo, StockLine, StockResult


DATABASE = Path(__file__).resolve().parents[1] / "data" / "campus_customs.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def _array(value: str) -> list[str]:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


@lru_cache(maxsize=128)
def _cached_search_ids(query: str, limit: int) -> tuple[str, ...]:
    terms = [term.strip().lower() for term in query.split() if term.strip()]
    if not terms:
        return ()
    with _connect() as connection:
        rows = connection.execute("SELECT product_id, name, garment_type, description, colors, search_tags FROM catalogue ORDER BY name").fetchall()
    matches = []
    for row in rows:
        searchable = " ".join([row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]).lower()
        if all(term in searchable for term in terms):
            matches.append(row["product_id"])
        if len(matches) >= limit:
            break
    return tuple(matches)


def _card(row: sqlite3.Row) -> ProductCard:
    with _connect() as connection:
        inventory = connection.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (row["product_id"],)
        ).fetchall()
    available = [item["size"] for item in inventory if item["quantity"] > 0]
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        price=row["price"],
        description=row["description"],
        image_url=f"/images/{row['image_file_path']}",
        colors=_array(row["colors"]),
        available_sizes=available,
        total_stock=sum(item["quantity"] for item in inventory),
    )


def search_catalogue(query: str, limit: int = 6) -> list[ProductCard]:
    """Search catalogue names, types, descriptions, colors, and tags."""
    bounded_limit = max(1, min(limit, 12))
    products = [product for product_id in _cached_search_ids(query, bounded_limit) if (product := get_product(product_id))]
    audit_event("tool_call", tool_name="search_catalogue", args={"query": query, "limit": bounded_limit}, result={"match_count": len(products), "product_ids": [product.product_id for product in products]})
    return products


def get_product(product_id: str) -> ProductCard | None:
    """Fetch one catalogue item with its current aggregate stock."""
    with _connect() as connection:
        row = connection.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    product = _card(row) if row else None
    audit_event("tool_call", tool_name="get_product", args={"product_id": product_id}, result={"found": product is not None, "product_id": product.product_id if product else None})
    return product


def lookup_product_info(product_id: str) -> ProductInfo | None:
    """Look up the catalogue description, price, colors, and image for one product."""
    with _connect() as connection:
        row = connection.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    if row is None:
        audit_event("tool_call", tool_name="lookup_product_info", args={"product_id": product_id}, result={"found": False})
        return None
    product = ProductInfo(
        product_id=row["product_id"], name=row["name"], garment_type=row["garment_type"],
        description=row["description"], price=row["price"], colors=_array(row["colors"]),
        image_url=f"/images/{row['image_file_path']}",
    )
    audit_event("tool_call", tool_name="lookup_product_info", args={"product_id": product_id}, result={"found": True, "price": product.price})
    return product


def lookup_stock(product_id: str, size: str | None = None) -> StockResult | None:
    """Look up current inventory, optionally for one requested size."""
    with _connect() as connection:
        product = connection.execute("SELECT product_id, name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if product is None:
            audit_event("tool_call", tool_name="lookup_stock", args={"product_id": product_id, "size": size}, result={"found": False})
            return None
        inventory = connection.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (product_id,)).fetchall()
    normalized_size = size.strip().upper() if size else None
    selected = [row for row in inventory if normalized_size is None or row["size"].upper() == normalized_size]
    result = StockResult(
        product_id=product["product_id"], product_name=product["name"], requested_size=normalized_size,
        stock=[StockLine(size=row["size"], quantity=row["quantity"], in_stock=row["quantity"] > 0) for row in selected],
        total_stock=sum(row["quantity"] for row in inventory),
    )
    audit_event("tool_call", tool_name="lookup_stock", args={"product_id": product_id, "size": normalized_size}, result={"requested_rows": len(result.stock), "total_stock": result.total_stock, "stock": [line.model_dump() for line in result.stock]})
    return result
