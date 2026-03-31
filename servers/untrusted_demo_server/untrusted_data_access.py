import sqlite3
from pathlib import Path

from servers.untrusted_demo_server.schemas import UntrustedStrategyRecord


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "untrusted_demo.db"


class UntrustedDataAccess:
    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = str(db_path)

    def get_customer_strategy(self, customer_id: str) -> UntrustedStrategyRecord | None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    customer_id,
                    account_priority,
                    strategic_note,
                    recommended_next_step,
                    instruction_like_text,
                    source_label,
                    last_updated
                FROM customer_strategy
                WHERE customer_id = ?
                """,
                (customer_id,),
            )

            row = cursor.fetchone()
            if row is None:
                return None

            return UntrustedStrategyRecord(**dict(row))
        finally:
            conn.close()
