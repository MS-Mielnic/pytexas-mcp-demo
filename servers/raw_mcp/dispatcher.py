from servers.raw_mcp.handlers import handle_read_customer_data, handle_send_email


TOOL_HANDLERS = {
    "read_customer_data": handle_read_customer_data,
    "send_email": handle_send_email,
}


def dispatch_tool_call(tool_name: str, arguments: dict) -> dict:
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Unknown tool: {tool_name}",
                }
            ],
        }

    return handler(arguments)
