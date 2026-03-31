from pathlib import Path
import json

from shared.config import settings

def policy_decision(allowed: bool, reason: str, decision_type: str = "allowed") -> dict:
    return {
        "allowed": allowed,
        "reason": reason,
        "type": decision_type,  # allowed | denied | rate_limited
    }

def load_allowed_domains() -> set[str]:
    path = Path("data/seed/allowed_domains.json")
    with path.open("r", encoding="utf-8") as f:
        domains = json.load(f)
    return set(domains)


def is_internal_email(email: str) -> bool:
    if "@" not in email:
        return False
    domain = email.split("@", 1)[1].lower()
    allowed_domains = load_allowed_domains()
    return domain in allowed_domains or domain == settings.internal_email_domain.lower()


def contains_sensitive_data(content: str) -> bool:
    lowered = content.lower()
    sensitive_markers = ["ssn", "social security", "ssn_last4"]
    return any(marker in lowered for marker in sensitive_markers)


def can_send_email(to: str, content: str) -> tuple[bool, str]:
    if not is_internal_email(to):
        return policy_decision(False, "External email domains are not allowed.","denied")

    if contains_sensitive_data(content):
        return policy_decision(False, "External email domains are not allowed.","denied")

    return policy_decision(True, "Allowed.", "allowed")

def can_update_customer_strategy(
    *,
    customer_id: str,
    strategy_summary: str,
    recommended_next_step: str,
    risk_flags: list[str],
) -> tuple[bool, str]:
    if not customer_id.strip():
        return policy_decision(False, "customer_id is required.", "denied")

    if not strategy_summary.strip():
        return policy_decision(False, "customer_id is required.", "denied")

    if not recommended_next_step.strip():
        return policy_decision(False, "customer_id is required.", "denied")

    if risk_flags:
        return policy_decision(False, "Customer strategy update blocked due to risk flags.", "denied")

    lowered_next = recommended_next_step.lower()
    if "send an email" in lowered_next or "email " in lowered_next:
        return policy_decision(False, "Customer strategy update contains disallowed action chaining.", "denied")


    if len(strategy_summary) > 500:
        return policy_decision(False, "strategy_summary exceeds maximum length.", "denied")


    if len(recommended_next_step) > 300:
        return policy_decision(False, "strategy_summary exceeds maximum length.", "denied")


    return policy_decision(True, "Allowed.", "allowed")
