from agent.models import (
    ExternalStrategyRaw,
    ExternalStrategySanitized,
)


SUSPICIOUS_KEYWORDS = [
    "email",
    "send",
    "contact",
    "immediately",
    "urgent",
    "escalate",
    "use the internal",
]


def validate_external_strategy(
    raw: ExternalStrategyRaw,
) -> ExternalStrategySanitized:
    risk_flags = []
    removed_fields = []


    instruction = (raw.instruction_like_text or "").lower()

    # Detect risky instruction-like content
    if any(keyword in instruction for keyword in SUSPICIOUS_KEYWORDS):
        risk_flags.append("instruction_like_text_detected")
        removed_fields.append("instruction_like_text")

    return ExternalStrategySanitized(
        customer_id=raw.customer_id,
        account_priority=raw.account_priority,
        strategic_note=raw.strategic_note,
        recommended_next_step=raw.recommended_next_step,
        risk_flags=risk_flags,
        removed_fields=removed_fields,
    )
