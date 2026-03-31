from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "orders.db"  # adjust if needed


def create_table(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_strategy_updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            strategy_summary TEXT NOT NULL,
            recommended_next_step TEXT NOT NULL,
            source_label TEXT NOT NULL,
            risk_flags TEXT NOT NULL,
            removed_fields TEXT NOT NULL,
            actor_type TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            approval_required INTEGER NOT NULL,
            approval_granted INTEGER,
            review_status TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()


def main():
    print("🛠️ Creating customer_strategy_updates table...")

    conn = sqlite3.connect(DB_PATH)

    try:
        create_table(conn)
        print("✅ Table created successfully (or already exists).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
