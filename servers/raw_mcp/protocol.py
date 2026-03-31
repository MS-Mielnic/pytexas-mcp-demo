TOOLS = [
    {
        "name": "read_customer_data",
        "description": "Read customer data by customer_id. Sensitive fields are sanitized.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Unique customer identifier",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an internal email. External recipients and sensitive content are blocked.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address",
                },
                "content": {
                    "type": "string",
                    "description": "Email body content",
                },
            },
            "required": ["to", "content"],
        },
    },
]


def handle_list_tools() -> dict:
    return {"tools": TOOLS}
