from shared.audit import write_audit_event
from shared.db import get_db_connection
from shared.sanitize import sanitize_customer_data
from time import perf_counter

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


def read_customer_data(customer_id: str, implementation: str = "shared") -> dict | None:
    start = perf_counter()
    customer = get_customer_by_id(customer_id)
    latency_ms = round((perf_counter() - start) * 1000, 3)

    if customer is None:
        write_audit_event(
            tool_name="read_customer_data",
            arguments={"customer_id": customer_id},
            sanitized_arguments={"customer_id": customer_id},
            policy_decision="allowed",
            result_status="not_found",
            error_message="Customer not found.",
            latency_ms=latency_ms,
            event_type="tool_not_found",
            implementation=implementation,
        )
        return None

    sanitized = sanitize_customer_data(customer)

    write_audit_event(
        tool_name="read_customer_data",
        arguments={"customer_id": customer_id},
        sanitized_arguments={"customer_id": customer_id},
        policy_decision="allowed",
        result_status="success",
        latency_ms=latency_ms,
        event_type="tool_success",
        implementation=implementation,
    )

    return sanitized
