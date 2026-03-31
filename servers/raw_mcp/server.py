import json
import sys

from shared.audit import write_protocol_log
from servers.raw_mcp.dispatcher import dispatch_tool_call
from servers.raw_mcp.protocol import handle_list_tools


def success_response(request_id, result: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def error_response(request_id, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": message,
        },
    }


def handle_request(request: dict) -> dict | None:
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        return success_response(
            request_id,
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "pytexas-raw-mcp-demo",
                    "version": "0.1.0",
                },
            },
        )

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return success_response(request_id, handle_list_tools())

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        return success_response(request_id, dispatch_tool_call(tool_name, arguments))

    return error_response(request_id, f"Unknown method: {method}")


def main() -> None:
    write_protocol_log("raw_server_start | implementation=raw | server starting")
    write_protocol_log("raw_session_open | implementation=raw | stdin loop ready")

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            write_protocol_log(
                f"raw_request_received | implementation=raw | payload={line}"
            )

            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            tool_name = params.get("name")

            if method == "tools/call" and tool_name:
                write_protocol_log(
                    f"raw_tool_call_start | implementation=raw | tool={tool_name}"
                )

            response = handle_request(request)

            if method == "tools/call" and tool_name:
                write_protocol_log(
                    f"raw_tool_call_end | implementation=raw | tool={tool_name}"
                )

            response_json = json.dumps(response)

            write_protocol_log(
                f"raw_response_sent | implementation=raw | response={response_json}"
            )

            print(response_json, flush=True)

    except KeyboardInterrupt:
        write_protocol_log(
            "raw_server_interrupt | implementation=raw | server interrupted by keyboard"
        )
    finally:
        write_protocol_log("raw_session_close | implementation=raw | stdin loop closed")
        write_protocol_log("raw_server_stop | implementation=raw | server stopped")


if __name__ == "__main__":
    main()
