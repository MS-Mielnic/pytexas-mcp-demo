from agent.client import fetch_untrusted_customer_strategy, call_ollama
from agent.validator import validate_external_strategy
from agent.models import ApprovalRequest
from agent.approval import request_approval
from agent.internal_client import send_internal_email, update_internal_customer_strategy
from agent.decision import parse_llm_decision
from agent.policy import is_allowed_action, requires_human_approval


def run_customer_strategy_workflow(customer_id: str, verbose: bool = False) -> dict:
    raw = fetch_untrusted_customer_strategy(customer_id)

    if raw is None:
        return {
            "customer_id": customer_id,
            "raw": None,
            "sanitized": None,
            "llm_response": None,
            "decision": None,
            "approval_required": False,
            "approval_granted": None,
            "action_executed": None,
            "message": "Customer not found.",
        }

    sanitized = validate_external_strategy(raw)

    prompt = f"""
Customer ID: {sanitized.customer_id}
Priority: {sanitized.account_priority}
Context: {sanitized.strategic_note}
Suggested next step: {sanitized.recommended_next_step}
Risk flags: {sanitized.risk_flags}
Removed fields: {sanitized.removed_fields}

Analyze this situation and recommend a safe next action.
"""

    try:
        llm_response = call_ollama(prompt)
        if verbose:
            print("\nRAW LLM RESPONSE:\n")
            print(llm_response)

        decision = parse_llm_decision(llm_response)
    except Exception as e:
        if verbose:
            print(f"LLM processing failed: {e}")
        return {
            "customer_id": customer_id,
            "raw": raw.model_dump(),
            "sanitized": sanitized.model_dump(),
            "llm_response": None,
            "decision": None,
            "approval_required": False,
            "approval_granted": None,
            "action_executed": None,
            "message": f"LLM processing failed: {e}",
        }

    if verbose:
        print("\nLLM DECISION:\n")
        print(decision)

    action = decision.recommended_action
    approval_required = False
    approval_granted = None
    action_executed = None
    message = "No action executed."

    if not is_allowed_action(action):
        message = f"Action '{action}' is not allowed by policy."
        if verbose:
            print(message)
        return {
            "customer_id": customer_id,
            "raw": raw.model_dump(),
            "sanitized": sanitized.model_dump(),
            "llm_response": llm_response,
            "decision": decision.model_dump(),
            "approval_required": False,
            "approval_granted": None,
            "action_executed": None,
            "message": message,
        }

    if requires_human_approval(action):
        approval_required = True
        if verbose:
            print(f"Policy override: action '{action}' requires human approval.")

        if action == "send_email":
            approval_request = ApprovalRequest(
                action=action,
                target="alice.johnson@company.local",
                content="Follow up on customer strategy review.",
                reason="Policy requires approval for sensitive trusted actions.",
            )
        elif action == "update_strategy":
            approval_request = ApprovalRequest(
                action=action,
                target=sanitized.customer_id,
                content="Store sanitized strategy update in trusted internal system.",
                reason="Policy requires approval for sensitive trusted actions.",
            )
        else:
            approval_request = ApprovalRequest(
                action=action,
                target="unknown",
                content="Requested sensitive action.",
                reason="Policy requires approval for sensitive trusted actions.",
            )

        approval_granted = request_approval(approval_request)

        if not approval_granted:
            message = "Action blocked due to lack of approval."
            if verbose:
                print(message)
            return {
                "customer_id": customer_id,
                "raw": raw.model_dump(),
                "sanitized": sanitized.model_dump(),
                "llm_response": llm_response,
                "decision": decision.model_dump(),
                "approval_required": approval_required,
                "approval_granted": approval_granted,
                "action_executed": None,
                "message": message,
            }

    if action == "send_email":
        result = send_internal_email(
            "alice.johnson@company.local",
            "Follow up on customer strategy review.",
        )
        if verbose:
            print(result)
        action_executed = "send_email"
        message = result

    elif action == "update_strategy":
        result = update_internal_customer_strategy(
            customer_id=sanitized.customer_id,
            strategy_summary=sanitized.strategic_note,
            recommended_next_step=sanitized.recommended_next_step,
            source_label=raw.source_label,
            risk_flags=sanitized.risk_flags,
            removed_fields=sanitized.removed_fields,
        )
        if verbose:
            print(result)
        action_executed = "update_strategy"
        message = result["message"]

    return {
        "customer_id": customer_id,
        "raw": raw.model_dump(),
        "sanitized": sanitized.model_dump(),
        "llm_response": llm_response,
        "decision": decision.model_dump(),
        "approval_required": approval_required,
        "approval_granted": approval_granted,
        "action_executed": action_executed,
        "message": message,
    }