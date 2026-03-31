from mcp.server.fastmcp import FastMCP

from shared.audit import write_protocol_log
from servers.untrusted_demo_server.middleware import log_middleware_event
from servers.untrusted_demo_server.schemas import LookupCustomerStrategyResult
from servers.untrusted_demo_server.untrusted_data_access import UntrustedDataAccess

mcp = FastMCP("pytexas-untrusted-demo")


@mcp.tool()
def lookup_customer_strategy(customer_id: str) -> LookupCustomerStrategyResult:
    """Read customer strategy data by customer_id from an untrusted external source."""
    log_middleware_event(
        "fastmcp_tool_call_start",
        f"tool=lookup_customer_strategy customer_id={customer_id}",
    )
    log_middleware_event(
        "fastmcp_tool_request",
        f"tool=lookup_customer_strategy customer_id={customer_id}",
    )

    try:
       # data_access = UntrustedDataAccess()
        result = UntrustedDataAccess().get_customer_strategy(customer_id)

        if result is None:
            response = LookupCustomerStrategyResult(
                found=False,
                record=None,
                message=f"Customer strategy '{customer_id}' not found.",
            )
            log_middleware_event(
                "fastmcp_tool_call_end",
                "tool=lookup_customer_strategy outcome=not_found",
            )
            log_middleware_event(
                "fastmcp_tool_response",
                "tool=lookup_customer_strategy outcome=not_found",
            )
            return response

        response = LookupCustomerStrategyResult(
            found=True,
            record=result,
            message="Customer strategy found.",
        )
        log_middleware_event(
            "fastmcp_tool_call_end",
            "tool=lookup_customer_strategy outcome=success",
        )
        log_middleware_event(
            "fastmcp_tool_response",
            "tool=lookup_customer_strategy outcome=success",
        )
        return response

    except Exception as exc:
        log_middleware_event(
            "fastmcp_error",
            f"tool=lookup_customer_strategy error={exc}",
        )
        raise


if __name__ == "__main__":
    print("Starting FastMCP server: pytexas-untrusted-demo")
    write_protocol_log("FastMCP server starting: pytexas-untrusted-demo")
    log_middleware_event("fastmcp_server_start", "server bootstrap")

    try:
        mcp.run()
    except KeyboardInterrupt:
        log_middleware_event(
            "fastmcp_server_interrupt",
            "server interrupted by keyboard",
        )
        write_protocol_log("FastMCP server interrupted (Ctrl+C)")
        print("FastMCP server interrupted.")
    finally:
        log_middleware_event("fastmcp_server_stop", "server shutdown complete")
        write_protocol_log("FastMCP server stopped")
