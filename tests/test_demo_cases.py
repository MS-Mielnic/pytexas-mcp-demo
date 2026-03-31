#this test the workflow, not the llm decision, we are testing orchestration(workflow) fetch untrusted data,sanitize it
#call LLM,parse decision,apply policy,request approval,execute trusted action

import json

from agent.workflow import run_customer_strategy_workflow


def test_cust_002_untrusted_instruction_neutralized(monkeypatch):
    monkeypatch.setattr(
        "agent.workflow.call_ollama",
        lambda prompt: json.dumps(
            {
                "summary": "Customer cust_002 is interested in reducing alert fatigue and improving incident triage.",
                "risks": ["instruction_like_text_detected"],
                "recommended_action": "none",
                "requires_approval": True,
            }
        ),
    )

    result = run_customer_strategy_workflow("cust_002")

    assert result["customer_id"] == "cust_002"
    assert "instruction_like_text" in result["raw"]
    assert "instruction_like_text" not in result["sanitized"]
    assert result["sanitized"]["risk_flags"] == ["instruction_like_text_detected"]
    assert result["sanitized"]["removed_fields"] == ["instruction_like_text"]

    assert result["decision"]["recommended_action"] == "none"
    assert result["approval_required"] is False
    assert result["approval_granted"] is None
    assert result["action_executed"] is None
    assert result["message"] == "No action executed."


def test_cust_001_safe_path_requires_approval_and_executes(monkeypatch):
    monkeypatch.setattr(
        "agent.workflow.call_ollama",
        lambda prompt: json.dumps(
            {
                "summary": "Customer cust_001 is a good candidate for a follow-up.",
                "risks": [],
                "recommended_action": "send_email",
                "requires_approval": False,
            }
        ),
    )
    monkeypatch.setattr("agent.workflow.request_approval", lambda request: True)
    monkeypatch.setattr(
        "agent.workflow.send_internal_email",
        lambda to, content: "Email sent successfully (simulated).",
    )

    result = run_customer_strategy_workflow("cust_001")

    assert result["customer_id"] == "cust_001"
    assert result["sanitized"]["risk_flags"] == []
    assert result["sanitized"]["removed_fields"] == []

    assert result["decision"]["recommended_action"] == "send_email"
    assert result["approval_required"] is True
    assert result["approval_granted"] is True
    assert result["action_executed"] == "send_email"
    assert result["message"] == "Email sent successfully (simulated)."
