import json
import sqlite3
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SEED_FILE = DATA_DIR / "seed" / "untrusted_accounts.json"
DB_FILE = DATA_DIR / "untrusted_demo.db"


def load_seed_data():
    with open(SEED_FILE, "r") as f:
        return json.load(f)


def reset_database(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Drop table if exists (clean reset)
    cursor.execute("DROP TABLE IF EXISTS customer_strategy")

    # Create table
    cursor.execute(
        """
        CREATE TABLE customer_strategy (
            customer_id TEXT PRIMARY KEY,
            account_priority TEXT,
            strategic_note TEXT,
            recommended_next_step TEXT,
            instruction_like_text TEXT,
            source_label TEXT,
            last_updated TEXT
        )
        """
    )

    conn.commit()


def insert_seed_data(conn: sqlite3.Connection, records: list[dict]):
    cursor = conn.cursor()

    for record in records:
        cursor.execute(
            """
            INSERT INTO customer_strategy (
                customer_id,
                account_priority,
                strategic_note,
                recommended_next_step,
                instruction_like_text,
                source_label,
                last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["customer_id"],
                record["account_priority"],
                record["strategic_note"],
                record["recommended_next_step"],
                record.get("instruction_like_text"),
                record["source_label"],
                record["last_updated"],
            ),
        )

    conn.commit()


def main():
    print("🌱 Seeding untrusted demo database...")

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Load seed data
    records = load_seed_data()
    print(f"Loaded {len(records)} records from seed file")

    # Connect to DB
    conn = sqlite3.connect(DB_FILE)

    # Reset schema
    reset_database(conn)
    print("Database schema reset")

    # Insert data
    insert_seed_data(conn, records)
    print("Data inserted successfully")

    conn.close()

    print(f"✅ Done. DB available at: {DB_FILE}")


if __name__ == "__main__":
    main()
