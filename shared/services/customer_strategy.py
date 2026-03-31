from time import perf_counter

from shared.audit import write_audit_event
from shared.db import get_db_connection


def update_customer_strategy(
    customer_id: str,
    strategy_summary: str,
    recommended_next_step: str,
    source_label: str,
    risk_flags: list[str],
    removed_fields: list[str],
    actor_type: str,
    actor_id: str,
    approval_required: bool,
    approval_granted: bool | None,
    review_status: str,
    implementation: str = "shared",
) -> dict:
    start = perf_counter()

    arguments = {
        "customer_id": customer_id,
        "strategy_summary": strategy_summary,
        "recommended_next_step": recommended_next_step,
        "source_label": source_label,
        "risk_flags": risk_flags,
        "removed_fields": removed_fields,
    }

    sanitized_arguments = arguments.copy()

    execution_context = {
        "actor_type": actor_type,
        "actor_id": actor_id,
        "approval_required": approval_required,
        "approval_granted": approval_granted,
        "review_status": review_status,
    }

    provenance = {
        "source_label": source_label,
        "source_type": "agent_tool",
        "tool_name": "update_customer_strategy_tool",
    }

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO customer_strategy_updates (
                customer_id,
                strategy_summary,
                recommended_next_step,
                source_label,
                risk_flags,
                removed_fields,
                actor_type,
                actor_id,
                approval_required,
                approval_granted,
                review_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                strategy_summary,
                recommended_next_step,
                source_label,
                ",".join(risk_flags),
                ",".join(removed_fields),
                actor_type,
                actor_id,
                int(approval_required),
                None if approval_granted is None else int(approval_granted),
                review_status,
            ),
        )

        update_id = cur.lastrowid
        conn.commit()
        conn.close()

        latency_ms = round((perf_counter() - start) * 1000, 3)

        write_audit_event(
            tool_name="update_customer_strategy",
            arguments=arguments,
            sanitized_arguments=sanitized_arguments,
            execution_context=execution_context,
            provenance=provenance,
            policy_decision="allowed",
            result_status="success",
            latency_ms=latency_ms,
            event_type="tool_success",
            implementation=implementation,
        )

        return {
            "success": True,
            "message": "Customer strategy updated successfully.",
            "customer_id": customer_id,
            "update_id": update_id,
        }

    except Exception as e:
        latency_ms = round((perf_counter() - start) * 1000, 3)

        write_audit_event(
            tool_name="update_customer_strategy",
            arguments=arguments,
            sanitized_arguments=sanitized_arguments,
            execution_context=execution_context,
            provenance=provenance,
            policy_decision="allowed",
            result_status="error",
            error_message=str(e),
            latency_ms=latency_ms,
            event_type="tool_error",
            implementation=implementation,
        )

        return {
            "success": False,
            "message": str(e),
            "customer_id": customer_id,
            "update_id": None,
        }
