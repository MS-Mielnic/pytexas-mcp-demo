from pydantic import BaseModel, Field
from typing import List, Optional


class ExternalStrategyRaw(BaseModel):
    customer_id: str
    account_priority: str
    strategic_note: str
    recommended_next_step: str
    instruction_like_text: str | None = None
    source_label: str
    last_updated: str


class ExternalStrategySanitized(BaseModel):
    customer_id: str
    account_priority: str
    strategic_note: str
    recommended_next_step: str

    # What we removed or flagged
    risk_flags: List[str] = Field(default_factory=list)
    removed_fields: List[str] = Field(default_factory=list)


class AgentDecision(BaseModel):
    action: str
    reasoning: str
    requires_approval: bool


class ApprovalRequest(BaseModel):
    action: str
    target: Optional[str] = None
    content: Optional[str] = None
    reason: str
    risk_flags: list[str] | None = None
