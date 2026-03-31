import json
from typing import Literal
from pydantic import BaseModel, Field


AllowedAction = Literal["none", "send_email", "update_strategy", "other"]

class LLMDecision(BaseModel):
    summary: str
    risks: list[str] = Field(default_factory=list)
    recommended_action: AllowedAction
    requires_approval: bool


def parse_llm_decision(text: str) -> LLMDecision:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(text[start:end + 1])

    return LLMDecision(**data)
