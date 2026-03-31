#define schemas-what inspector will show and what the server enforces

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ---------
# TOOL INPUTS
# ---------

class ReadCustomerInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")


class CreateOrderInput(BaseModel):
    customer_id: str
    item: str
    amount: float


class SendEmailInput(BaseModel):
    to: str = Field(..., description="Recipient email address")
    content: str = Field(..., description="Email body content")


class GetLogsInput(BaseModel):
    service: str = Field(..., description="Service name to query logs from")


# ---------
# DOMAIN MODELS
# ---------

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    account_tier: str
    shipping_city: str
    ssn_last4: Optional[str] = None  # sensitive


class Order(BaseModel):
    order_id: str
    customer_id: str
    item: str
    amount: float
    status: str
    created_at: datetime


# ---------
# AUDIT
# ---------

class AuditEvent(BaseModel):
    request_id: str
    tool_name: str
    timestamp: datetime
    arguments: dict
    sanitized_arguments: dict
    policy_decision: str
    result_status: str
    error_message: Optional[str] = None

# -------
# FORMAT RESPONSE
# -------
class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    account_tier: str
    shipping_city: str
    ssn_last4: str

class CustomerLookupResult(BaseModel):
    found: bool
    customer: CustomerResponse | None = None
    message: str
