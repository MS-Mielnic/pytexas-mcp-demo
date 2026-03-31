from agent.policy import is_allowed_action, requires_human_approval
from agent.decision import parse_llm_decision


def test_policy_rules():
    assert is_allowed_action("send_email") is True
    assert is_allowed_action("delete_customer") is False
    assert requires_human_approval("send_email") is True
    assert requires_human_approval("none") is False


def test_decision_parser():
    sample = """
    {
      "summary": "Customer is high priority.",
      "risks": ["external instruction detected"],
      "recommended_action": "send_email",
      "requires_approval": true
    }
    """

    decision = parse_llm_decision(sample)

    assert decision.recommended_action == "send_email"
    assert decision.requires_approval is True
