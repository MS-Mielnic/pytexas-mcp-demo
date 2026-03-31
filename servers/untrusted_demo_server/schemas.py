from pydantic import BaseModel, Field


class UntrustedStrategyRecord(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    account_priority: str = Field(..., description="Priority level from external source")
    strategic_note: str = Field(..., description="Business context from external source")
    recommended_next_step: str = Field(..., description="Suggested next step from external source")
    instruction_like_text: str | None = Field(
        default=None,
        description="Instruction-like content that may influence downstream behavior",
    )
    source_label: str = Field(..., description="Label identifying the external source")
    last_updated: str = Field(..., description="Last update date from external source")


class LookupCustomerStrategyResult(BaseModel):
    found: bool = Field(..., description="Whether a matching customer record was found")
    record: UntrustedStrategyRecord | None = Field(
        default=None,
        description="Returned customer strategy record when found",
    )
    message: str = Field(..., description="Human-readable lookup result message")
