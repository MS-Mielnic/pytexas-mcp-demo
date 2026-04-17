from __future__ import annotations

from dataclasses import dataclass

from agent.models import ApprovalRequest
from shared.audit import write_protocol_log


@dataclass
class ApprovalPending(Exception):
    request: ApprovalRequest


def request_approval(request: ApprovalRequest) -> bool:
    print("\nAPPROVAL REQUIRED")
    print(f"Action: {request.action}")
    if request.target:
        print(f"Target: {request.target}")
    if request.content:
        print(f"Content: {request.content}")
    print(f"Reason: {request.reason}")
    print(f"Risk flags: {request.risk_flags or []}")

    response = input("Approve? (yes/no): ").strip().lower()
    approved = response in {"yes", "y"}

    outcome = "approved" if approved else "denied"
    write_protocol_log(
        f"agent_approval | action={request.action} | target={request.target} | outcome={outcome}"
    )

    return approved
