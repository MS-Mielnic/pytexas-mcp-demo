# lookup helper for send_email_demo case

def get_contact_email(customer_id: str) -> str:
    """
    Return the approved contact email for a given demo customer.

    This is trusted/internal mapping data, not data from the untrusted MCP server.
    """

    contact_map = {
        "cust_001": "alice.johnson@company.local",
        "cust_002": "bob.smith@company.local",
        "cust_003": "david.lee@company.local",
        "cust_email_demo": "alice.johnson@company.local",
        # Optional external-policy test case:
        # "cust_email_external": "carol.lee@external-demo.com",
    }

    return contact_map.get(customer_id, "fallback@company.local")
