from shared.db import get_db_connection


def get_customer_by_id(customer_id: str) -> dict | None:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT customer_id, name, email, account_tier, shipping_city, ssn_last4
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,),
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)
