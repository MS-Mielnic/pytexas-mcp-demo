#create mcp server tool handler
import json

from shared.schemas import ReadCustomerInput, SendEmailInput
from shared.services.customers import read_customer_data
from shared.services.email import send_email


def handle_read_customer_data(arguments: dict) -> dict:
    payload = ReadCustomerInput(**arguments)
    result = read_customer_data(payload.customer_id, implementation="raw")

    if result is None:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Customer '{payload.customer_id}' not found.",
                }
            ],
        }

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2),
            }
        ]
    }


def handle_send_email(arguments: dict) -> dict:
    payload = SendEmailInput(**arguments)
    result = send_email(payload.to, payload.content, implementation="raw")

    if not result["success"]:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": result["message"],
                }
            ],
        }

    return {
        "content": [
            {
                "type": "text",
                "text": result["message"],
            }
        ]
    }
