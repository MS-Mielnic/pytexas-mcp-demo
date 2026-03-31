from mcp.server.fastmcp import FastMCP

from shared.audit import write_protocol_log, write_audit_event
from shared.schemas import CustomerLookupResult, CustomerResponse
from shared.services.customers import read_customer_data as read_customer_service
from shared.services.email import send_email as send_email_service
from servers.fastmcp_server.middleware import log_middleware_event
from shared.services.customer_strategy import update_customer_strategy
from shared.policy import can_update_customer_strategy
from time import time


_trusted_approval_context = {
    "approval_required": False,
    "approval_granted": None,
    "review_status": "direct_call",
    "approval_source": "none",
}

def set_trusted_approval_context(
    approval_required: bool,
    approval_granted: bool | None,
    review_status: str,
    approval_source: str = "workflow",
) -> None:
    global _trusted_approval_context
    _trusted_approval_context = {
        "approval_required": approval_required,
        "approval_granted": approval_granted,
        "review_status": review_status,
        "approval_source": approval_source,
    }

def clear_trusted_approval_context() -> None:
    global _trusted_approval_context
    _trusted_approval_context = {
        "approval_required": False,
        "approval_granted": None,
        "review_status": "direct_call",
        "approval_source": "none",
    }


# simple in-memory rate limiter
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_CALLS = 3
_rate_limit_store = {}

def is_rate_limited(tool_name: str, key: str) -> bool:
    now = time()
    window_start = now - RATE_LIMIT_WINDOW

    calls = _rate_limit_store.get((tool_name, key), [])

    # keep only calls within window
    calls = [t for t in calls if t > window_start]

    if len(calls) >= RATE_LIMIT_MAX_CALLS:
        _rate_limit_store[(tool_name, key)] = calls
        return True

    calls.append(now)
    _rate_limit_store[(tool_name, key)] = calls
    return False


mcp = FastMCP("pytexas-fastmcp-demo")


@mcp.tool()
def read_customer_data(customer_id: str) -> CustomerLookupResult:
    """Read customer data by customer_id. Sensitive fields are sanitized."""
    log_middleware_event(
        "fastmcp_tool_call_start",
        f"tool=read_customer_data customer_id={customer_id}",
    )
    log_middleware_event(
        "fastmcp_tool_request",
        f"tool=read_customer_data customer_id={customer_id}",
    )

    try:
        result = read_customer_service(customer_id, implementation="fastmcp")

        if result is None:
            response = CustomerLookupResult(
                found=False,
                customer=None,
                message=f"Customer '{customer_id}' not found.",
            )
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=read_customer_data outcome=not_found",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=read_customer_data outcome=not_found",
            )
            return response

        response = CustomerLookupResult(
            found=True,
            customer=CustomerResponse(**result),
            message="Customer found.",
        )
        log_middleware_event(
            "fastmcp_tool_call_end",
            "tool=read_customer_data outcome=success",
        )
        log_middleware_event(
            "fastmcp_tool_response",
            "tool=read_customer_data outcome=success",
        )
        return response

    except Exception as exc:
        log_middleware_event(
            "fastmcp_error",
            f"tool=read_customer_data error={exc}",
        )
        raise


@mcp.tool()
def send_email_tool(to: str, content: str) -> str:
    """Send an internal email. External recipients and sensitive content are blocked."""
    log_middleware_event(
        "fastmcp_tool_call_start",
        f"tool=send_email_tool to={to}",
    )
    log_middleware_event(
        "fastmcp_tool_request",
        f"tool=send_email_tool to={to}",
    )

    try:
        result = send_email_service(to, content, implementation="fastmcp")

        if result["success"]:
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=send_email_tool outcome=success",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=send_email_tool outcome=success",
            )
        else:
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=send_email_tool outcome=denied",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=send_email_tool outcome=denied",
            )

        return result["message"]

    except Exception as exc:
        log_middleware_event(
            "fastmcp_error",
            f"tool=send_email_tool error={exc}",
        )
        raise


@mcp.tool()
def raise_demo_error() -> str:
    """Temporary demo tool that raises an exception to test middleware error logging."""
    log_middleware_event(
         "fastmcp_tool_call_start",
         "tool=raise_demo_error",
    )

    log_middleware_event(
        "fastmcp_tool_request",
        "tool=raise_demo_error",
    )

    try:
        raise RuntimeError("Intentional demo error from FastMCP tool")
    except Exception as exc:
        log_middleware_event(
            "fastmcp_error",
            f"tool=raise_demo_error error={exc}",
        )
        raise


@mcp.tool()
def update_customer_strategy_tool(
    customer_id: str,
    strategy_summary: str,
    recommended_next_step: str,
    source_label: str,
    risk_flags: list[str],
    removed_fields: list[str],
):
    """Tool that enriches the secure db by updating the account strategy from the data exposed by the unsecure mcp server"""

    log_middleware_event(
        "fastmcp_tool_call_start",
        f"tool=update_customer_strategy_tool customer_id={customer_id}",
    )
    log_middleware_event(
        "fastmcp_tool_request",
        f"tool=update_customer_strategy_tool customer_id={customer_id}",
    )

    try:
        actor_id = "fastmcp_server"
        actor_type = "agent"
        approval_required = _trusted_approval_context["approval_required"]
        approval_granted = _trusted_approval_context["approval_granted"]
        review_status = _trusted_approval_context["review_status"]

        decision = can_update_customer_strategy(
            customer_id=customer_id,
            strategy_summary=strategy_summary,
            recommended_next_step=recommended_next_step,
            risk_flags=risk_flags,
        )

        # DENIED path
        if not decision["allowed"]:
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=update_customer_strategy_tool outcome=denied",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=update_customer_strategy_tool outcome=denied",
            )

            write_audit_event(
                tool_name="update_customer_strategy",
                arguments={
                    "customer_id": customer_id,
                    "strategy_summary": strategy_summary,
                    "recommended_next_step": recommended_next_step,
                    "source_label": source_label,
                    "risk_flags": risk_flags,
                    "removed_fields": removed_fields,
                },
                sanitized_arguments={
                    "customer_id": customer_id,
                    "strategy_summary": strategy_summary,
                    "recommended_next_step": recommended_next_step,
                    "source_label": source_label,
                    "risk_flags": risk_flags,
                    "removed_fields": removed_fields,
                },
                policy_decision="allowed",
                result_status="denied",
                error_message=decision["reason"],
                event_type="tool_denied",
                implementation="fastmcp",
                execution_context={
                    "actor_type": actor_type,
                    "actor_id": actor_id,
                    "approval_required": approval_required,
                    "approval_granted": approval_granted,
                    "review_status": review_status,
                },
                provenance={
                    "source_type": "agent_tool",
                    "tool_name": "update_customer_strategy_tool",
                },
            )

            return {
                "success": False,
                "message": decision["reason"]
            }

        # RATE LIMIT CHECK
        if is_rate_limited("update_customer_strategy_tool", customer_id):
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=update_customer_strategy_tool outcome=rate_limited",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=update_customer_strategy_tool outcome=rate_limited",
            )

            write_audit_event(
                tool_name="update_customer_strategy",
                arguments={
                    "customer_id": customer_id,
                    "strategy_summary": strategy_summary,
                    "recommended_next_step": recommended_next_step,
                    "source_label": source_label,
                    "risk_flags": risk_flags,
                    "removed_fields": removed_fields,
                },
                sanitized_arguments={
                    "customer_id": customer_id,
                    "strategy_summary": strategy_summary,
                    "recommended_next_step": recommended_next_step,
                    "source_label": source_label,
                    "risk_flags": risk_flags,
                    "removed_fields": removed_fields,
                },
                policy_decision="allowed",
                result_status="rate_limited",
                error_message="Rate limit exceeded for customer_strategy updates.",
                event_type="tool_rate_limited",
                implementation="fastmcp",
                execution_context={
                    "actor_type": actor_type,
                    "actor_id": actor_id,
                    "approval_required": approval_required,
                    "approval_granted": approval_granted,
                    "review_status": review_status,
                },
                provenance={
                    "source_type": "agent_tool",
                    "tool_name": "update_customer_strategy_tool",
                },
            )

            return {
                "success": False,
                "message": "Rate limit exceeded for customer_strategy updates.",
            }

        # SUCCESS path
        result = update_customer_strategy(
            customer_id=customer_id,
            strategy_summary=strategy_summary,
            recommended_next_step=recommended_next_step,
            source_label=source_label,
            risk_flags=risk_flags,
            removed_fields=removed_fields,
            actor_type=actor_type,
            actor_id=actor_id,
            approval_required=approval_required,
            approval_granted=approval_granted,
            review_status=review_status,
            implementation="fastmcp",
        )

        log_middleware_event(
            "fastmcp_tool_call_end",
            "tool=update_customer_strategy_tool outcome=success",
        )
        log_middleware_event(
            "fastmcp_tool_response",
            "tool=update_customer_strategy_tool outcome=success",
        )

        return result

    except Exception as exc:
        log_middleware_event(
            "fastmcp_error",
            f"tool=update_customer_strategy_tool error={exc}",
        )
        raise


if __name__ == "__main__":
    print("Starting FastMCP server: pytexas-fastmcp-demo")
    write_protocol_log("FastMCP server starting: pytexas-fastmcp-demo")
    log_middleware_event("fastmcp_server_start", "server bootstrap")

    try:
        mcp.run()
    except KeyboardInterrupt:
        log_middleware_event("fastmcp_server_interrupt", "server interrupted by keyboard")
        write_protocol_log("FastMCP server interrupted (Ctrl+C)")
        print("FastMCP server interrupted.")
    finally:
        log_middleware_event("fastmcp_server_stop", "server shutdown complete")
        write_protocol_log("FastMCP server stopped")