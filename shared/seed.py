import json
from pathlib import Path

from shared.db import get_db_connection


BASE_SEED_DIR = Path("data/seed")


def load_json_file(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def create_tables() -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            account_tier TEXT NOT NULL,
            shipping_city TEXT NOT NULL,
            ssn_last4 TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """
    )

    conn.commit()
    conn.close()


def clear_tables() -> None:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM customers")
    conn.commit()
    conn.close()


def seed_customers() -> None:
    customers = load_json_file(BASE_SEED_DIR / "customers.json")
    conn = get_db_connection()
    cur = conn.cursor()

    for customer in customers:
        cur.execute(
            """
            INSERT INTO customers (
                customer_id, name, email, account_tier, shipping_city, ssn_last4
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                customer["customer_id"],
                customer["name"],
                customer["email"],
                customer["account_tier"],
                customer["shipping_city"],
                customer.get("ssn_last4"),
            ),
        )

    conn.commit()
    conn.close()


def seed_orders() -> None:
    orders = load_json_file(BASE_SEED_DIR / "orders.json")
    conn = get_db_connection()
    cur = conn.cursor()

    for order in orders:
        cur.execute(
            """
            INSERT INTO orders (
                order_id, customer_id, item, amount, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order["order_id"],
                order["customer_id"],
                order["item"],
                order["amount"],
                order["status"],
                order["created_at"],
            ),
        )

    conn.commit()
    conn.close()


def reset_and_seed_db() -> None:
    create_tables()
    clear_tables()
    seed_customers()
    seed_orders()
