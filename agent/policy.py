ALLOWED_ACTIONS = {"send_email", "update_strategy", "none"}
SENSITIVE_ACTIONS = {"send_email", "update_strategy"}


def is_allowed_action(action: str) -> bool:
    return action in ALLOWED_ACTIONS


def requires_human_approval(action: str) -> bool:
    return action in SENSITIVE_ACTIONS
