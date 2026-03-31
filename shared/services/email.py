#logging email and customer_update tools into logs/audit/audit.jsonl

from time import perf_counter

from shared.audit import write_audit_event
from shared.policy import can_send_email


def send_email(to: str, content: str, implementation: str = "shared") -> dict:
    start = perf_counter()

    arguments = {
        "to": to,
        "content": content,
    }
    sanitized_arguments = arguments.copy()

    execution_context = {
        "actor_type": "agent",
        "actor_id": "fastmcp_server",
        "approval_required": True,
        "approval_granted": True,
        "review_status": "approved",
    }

    provenance = {
        "source_type": "agent_tool",
        "tool_name": "send_email_tool",
    }

    decision = can_send_email(to, content)

    if not decision["allowed"]:
        latency_ms = round((perf_counter() - start) * 1000, 3)
        write_audit_event(
            tool_name="send_email",
            arguments=arguments,
            sanitized_arguments=sanitized_arguments,
            execution_context=execution_context,
            provenance=provenance,
            policy_decision=decision["type"],
            result_status="denied",
            error_message=decision["reason"],
            latency_ms=latency_ms,
            event_type="tool_denied",
            implementation=implementation,
        )
        return {
            "success": False,
            "message": decision["reason"],
        }

    latency_ms = round((perf_counter() - start) * 1000, 3)
    write_audit_event(
        tool_name="send_email",
        arguments=arguments,
        sanitized_arguments=sanitized_arguments,
        execution_context=execution_context,
        provenance=provenance,
        policy_decision=decision["type"],
        result_status="success",
        latency_ms=latency_ms,
        event_type="tool_success",
        implementation=implementation,
    )

    return {
        "success": True,
        "message": f"Email sent to {to}",
    }
