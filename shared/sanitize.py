SENSITIVE_FIELDS = {"ssn_last4"}


def mask_value(value: str) -> str:
    if not value:
        return value
    return "*" * max(len(value) - 2, 0) + value[-2:]


def sanitize_customer_data(customer: dict) -> dict:
    sanitized = customer.copy()

    for field in SENSITIVE_FIELDS:
        if field in sanitized and sanitized[field] is not None:
            sanitized[field] = mask_value(str(sanitized[field]))

    return sanitized
