import csv
import io
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transactions.db")
REQUIRED = ["order_id", "order_date", "customer_id", "product", "category",
            "quantity", "unit_price", "payment_method", "status"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            order_id TEXT PRIMARY KEY,
            order_date TEXT NOT NULL,          -- YYYY-MM-DD
            customer_id TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            payment_method TEXT,
            status TEXT,                       -- Completed / Returned / Cancelled
            total REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_date ON transactions(order_date);
        """)


def import_csv(text):
    """Load CSV text into the database. Returns (imported, skipped)."""
    reader = csv.DictReader(io.StringIO(text))
    missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    rows, skipped = [], 0
    for r in reader:
        try:
            qty, price = int(r["quantity"]), float(r["unit_price"])
            datetime.strptime(r["order_date"].strip(), "%Y-%m-%d")
            if qty <= 0 or price < 0 or not r["order_id"].strip():
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            skipped += 1
            continue
        rows.append((r["order_id"].strip(), r["order_date"].strip(), r["customer_id"].strip(),
                     r["product"].strip(), r["category"].strip(), qty, price,
                     r["payment_method"].strip(), r["status"].strip().title(), round(qty * price, 2)))
    with get_db() as db:
        db.executemany("INSERT OR REPLACE INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    return len(rows), skipped
