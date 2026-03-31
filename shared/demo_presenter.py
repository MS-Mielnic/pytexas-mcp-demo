from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROTOCOL_LOG = Path("logs/protocol/protocol.log")
AUDIT_LOG = Path("logs/audit/audit.jsonl")


def _find_last_protocol_line_with_prefix(
    lines: list[str],
    prefix_token: str,
    *required_tokens: str,
) -> str | None:
    for line in reversed(lines):
        if prefix_token not in line:
            continue
        if all(token in line for token in required_tokens):
            return line
    return None


def _read_protocol_lines() -> list[str]:
    if not PROTOCOL_LOG.exists():
        return []
    return PROTOCOL_LOG.read_text(encoding="utf-8").splitlines()


def _read_audit_entries() -> list[dict[str, Any]]:
    if not AUDIT_LOG.exists():
        return []

    entries: list[dict[str, Any]] = []
    for line in AUDIT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _find_last_protocol_line(lines: list[str], *required_tokens: str) -> str | None:
    for line in reversed(lines):
        if all(token in line for token in required_tokens):
            return line
    return None


def _find_last_audit_entry(
    entries: list[dict[str, Any]], tool_name: str
) -> dict[str, Any] | None:
    for entry in reversed(entries):
        if entry.get("tool_name") == tool_name:
            return entry
    return None


def _extract_protocol_outcome(
    lines: list[str],
    implementation: str,
    tool: str,
    extra_tokens: list[str] | None = None,
) -> str | None:
    """
    Look for the most recent tool_call_end outcome for a given implementation/tool.
    Returns one of: success, blocked, denied, error, or None.
    """
    tokens = [
        "fastmcp_tool_call_end",
        f"implementation={implementation}",
        f"tool={tool}",
    ]
    if extra_tokens:
        tokens.extend(extra_tokens)

    for outcome in ("success", "blocked", "denied", "error"):
        line = _find_last_protocol_line_with_prefix(
            lines,
            "fastmcp_tool_call_end",
            f"implementation={implementation}",
            f"tool={tool}",
            f"outcome={outcome}",
            *(extra_tokens or []),
        )
        if line:
            return outcome

    return None


def _infer_execution_from_message(message: str | None) -> str | None:
    if not message:
        return None

    lowered = message.lower()

    if "blocked" in lowered:
        return "blocked"
    if "denied" in lowered:
        return "denied"
    if "failed" in lowered or "error" in lowered:
        return "error"
    if "success" in lowered or "sent" in lowered or "updated successfully" in lowered:
        return "success"

    return None


def _print_header(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print(f"{'=' * 72}")


def _print_kv(label: str, value: Any) -> None:
    print(f"{label}: {value}")


def render_demo_output(customer_id: str, result: dict[str, Any]) -> None:
    protocol_lines = _read_protocol_lines()
    audit_entries = _read_audit_entries()

    decision = result.get("decision") or {}
    sanitized = result.get("sanitized") or {}
    action = decision.get("recommended_action")
    action_executed = result.get("action_executed")
    final_message = result.get("message")

    print("\n============================================================")
    print("MCP SECURE AGENT DEMO")
    print("Trusted tools + untrusted enrichment")
    print("Same protocol, different trust")
    print("============================================================")

    _print_header("[1/6] FETCH UNTRUSTED DATA | Untrusted MCP server")
    lookup_start = _find_last_protocol_line_with_prefix(
        protocol_lines,
        "fastmcp_tool_call_start",
        "implementation=untrusted_demo",
        "tool=lookup_customer_strategy",
        f"customer_id={customer_id}",
    )
    lookup_end = _find_last_protocol_line_with_prefix(
        protocol_lines,
        "fastmcp_tool_call_end",
        "implementation=untrusted_demo",
        "tool=lookup_customer_strategy",
        "outcome=success",
    )

    _print_kv("source", "untrusted_demo")
    _print_kv("tool", "lookup_customer_strategy")
    _print_kv("customer_id", customer_id)
    _print_kv("lookup_started", "yes" if lookup_start else "no")
    _print_kv("lookup_result", "success" if lookup_end else "not_found")

    _print_header("[2/6] SANITIZE AND VALIDATE | Agent boundary")
    _print_kv("sanitizer_flags", sanitized.get("risk_flags", []))
    _print_kv("removed_fields", sanitized.get("removed_fields", []))
    _print_kv("priority", sanitized.get("account_priority"))
    _print_kv("recommended_next_step", sanitized.get("recommended_next_step"))

    _print_header("[3/6] AGENT DECISION | LLM llama3 inside agent")
    _print_kv("recommended_action", action)
    _print_kv("llm_risks", decision.get("risks", []))
    _print_kv("approval_required", result.get("approval_required"))
    _print_kv("approval_granted", result.get("approval_granted"))
    _print_kv("agent_result", final_message)

    _print_header("[4/6] POLICY AND APPROVAL | Agent policy gate")
    approval_line = None
    if action:
        approval_line = _find_last_protocol_line(
            protocol_lines,
            "agent_approval",
            f"action={action}",
        )

    if approval_line:
        target = (
            approval_line.split("target=")[-1].split(" | ")[0]
            if "target=" in approval_line
            else "unknown"
        )
        outcome = (
            approval_line.split("outcome=")[-1]
            if "outcome=" in approval_line
            else "unknown"
        )
        _print_kv("action", action)
        _print_kv("target", target)
        _print_kv("approval_outcome", outcome)
    else:
        _print_kv("approval_event", "not_required_or_not_found")

    _print_header("[5/6] TRUSTED ACTION | Trusted MCP server: fastmcp")
    trusted_tool = None
    trusted_target = None
    trusted_outcome = None

    if action_executed == "send_email":
        trusted_tool = "send_email_tool"
        start_line = _find_last_protocol_line_with_prefix(
            protocol_lines,
            "fastmcp_tool_call_start",
            "implementation=fastmcp",
            "tool=send_email_tool",
        )
        if start_line and "to=" in start_line:
            trusted_target = start_line.split("to=")[-1].strip()

        trusted_outcome = _extract_protocol_outcome(
            protocol_lines,
            implementation="fastmcp",
            tool="send_email_tool",
        )

    elif action_executed == "update_strategy":
        trusted_tool = "update_customer_strategy_tool"
        start_line = _find_last_protocol_line_with_prefix(
            protocol_lines,
            "fastmcp_tool_call_start",
            "implementation=fastmcp",
            "tool=update_customer_strategy_tool",
            f"customer_id={customer_id}",
        )
        if start_line:
            trusted_target = customer_id

        trusted_outcome = _extract_protocol_outcome(
            protocol_lines,
            implementation="fastmcp",
            tool="update_customer_strategy_tool",
            extra_tokens=[f"customer_id={customer_id}"],
        )

    if trusted_outcome is None and action_executed:
        trusted_outcome = _infer_execution_from_message(final_message)

    _print_kv("tool", trusted_tool or "none")
    _print_kv("target", trusted_target or "none")
    _print_kv("execution", trusted_outcome or "none")

    _print_header("[6/6] EVIDENCE WRITTEN | Audit + Protocol logs")
    audit_tool = None
    if action_executed == "send_email":
        audit_tool = "send_email"
    elif action_executed == "update_strategy":
        audit_tool = "update_customer_strategy"

    audit_entry = _find_last_audit_entry(audit_entries, audit_tool) if audit_tool else None

    if audit_entry:
        execution_context = audit_entry.get("execution_context") or {}
        provenance = audit_entry.get("provenance") or {}

        _print_kv("audit_tool_name", audit_entry.get("tool_name"))
        _print_kv("policy_decision", audit_entry.get("policy_decision"))
        _print_kv("result_status", audit_entry.get("result_status"))
        _print_kv("approval_required", execution_context.get("approval_required"))
        _print_kv("approval_granted", execution_context.get("approval_granted"))
        _print_kv("provenance_tool", provenance.get("tool_name"))
    else:
        _print_kv("audit_entry", "not_found")

    print("\n============================================================")
    print("RESULT")
    _print_kv("action_executed", action_executed or "none")
    _print_kv("final_message", final_message)
    print("\nKey takeaway:")
    print("Same protocol, different trust — enforced in code.")
    print("============================================================")