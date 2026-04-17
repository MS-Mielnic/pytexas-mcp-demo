from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.approval import ApprovalPending
from agent.workflow import run_customer_strategy_workflow


PROTOCOL_LOG = Path("logs/protocol/protocol.log")
AUDIT_LOG = Path("logs/audit/audit.jsonl")


def reset_logs() -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    PROTOCOL_LOG.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG.write_text("", encoding="utf-8")
    PROTOCOL_LOG.write_text("", encoding="utf-8")


def read_protocol_lines() -> list[str]:
    if not PROTOCOL_LOG.exists():
        return []
    return [
        line.strip()
        for line in PROTOCOL_LOG.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_audit_entries() -> list[dict[str, Any]]:
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


def show_kv(label: str, value: Any) -> None:
    st.markdown(f"**{label}:** `{value}`")


def section_box(
    title: str,
    subtitle: str,
    actor: str,
    content_fn: Callable[[], None],
) -> None:
    st.markdown(f"#### {title}")
    if subtitle:
        st.caption(subtitle)

    with st.container(border=True):
        if actor == "untrusted":
            st.error("🔴 UNTRUSTED MCP SERVER")
        elif actor == "agent":
            st.warning("🟡 AGENT")
        elif actor == "trusted":
            st.success("🔵 TRUSTED MCP SERVER")

        content_fn()


def streamlit_approval_handler(request):
    decision = st.session_state.get("approval_decision")

    if decision is None:
        st.session_state["pending_approval_request"] = request
        raise ApprovalPending(request)

    st.session_state["approval_decision"] = None
    return decision


def render_results(result: dict[str, Any]) -> None:
    decision = result.get("decision") or {}
    sanitized = result.get("sanitized") or {}
    action_executed = result.get("action_executed")
    final_message = result.get("message")

    st.markdown("## Demo Flow")

    st.markdown("### 🔴 Untrusted Input (External MCP)")

    def fetch_content() -> None:
        show_kv("customer_id", result.get("customer_id"))
        raw = result.get("raw")
        if raw:
            st.json(raw)
        else:
            st.info("No raw record returned.")

    section_box(
        "1) Fetch Untrusted Data",
        "Source: untrusted_demo (read-only, external)",
        "untrusted",
        fetch_content,
    )

    st.markdown("### 🟡 Agent (Boundary + Decision + Policy)")

    def sanitize_content() -> None:
        flags = sanitized.get("risk_flags", [])
        removed = sanitized.get("removed_fields", [])

        if flags:
            st.warning(f"Sanitizer flags: {flags}")
        else:
            st.success("No sanitizer flags.")

        show_kv("removed_fields", removed)
        show_kv("priority", sanitized.get("account_priority"))
        show_kv("recommended_next_step", sanitized.get("recommended_next_step"))

        if sanitized:
            with st.expander("Sanitized payload"):
                st.json(sanitized)

    section_box(
        "2) Sanitize and Validate",
        "Agent boundary: convert untrusted input into a safe representation",
        "agent",
        sanitize_content,
    )

    def decision_content() -> None:
        show_kv("recommended_action", decision.get("recommended_action"))
        show_kv("decision_summary", decision.get("summary"))
        show_kv("llm_risks", decision.get("risks", []))

    section_box(
        "3) Agent Decision (LLM)",
        "Model recommends an action (not executed yet)",
        "agent",
        decision_content,
    )

    def approval_content() -> None:
        show_kv("human_approval_required", result.get("approval_required"))
        show_kv("human_approval_granted", result.get("approval_granted"))

    section_box(
        "4) Policy Gate + Human Approval",
        "Agent policy decides if we can attempt; human approves or denies",
        "agent",
        approval_content,
    )

    st.markdown("### 🔵 Trusted Execution (Internal MCP)")

    def trusted_content() -> None:
        show_kv("action_attempted", action_executed)
        show_kv("trusted_execution_result", final_message)

        if final_message:
            lowered = str(final_message).lower()
            if "blocked" in lowered or "denied" in lowered:
                st.error(final_message)
            elif "success" in lowered or "sent" in lowered or "updated" in lowered:
                st.success(final_message)
            else:
                st.info(final_message)

    section_box(
        "5) Trusted Action",
        "Final enforcement and execution happens here",
        "trusted",
        trusted_content,
    )

    def evidence_content() -> None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Audit Log (structured)**")
            audit_entries = read_audit_entries()
            if audit_entries:
                df = pd.DataFrame(audit_entries)
                rename_map = {}
                if "policy_decision" in df.columns:
                    rename_map["policy_decision"] = "agent_policy_decision"
                if "result_status" in df.columns:
                    rename_map["result_status"] = "trusted_execution_result"
                if rename_map:
                    df = df.rename(columns=rename_map)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No audit entries yet.")

        with col2:
            st.markdown("**Protocol Log (event stream)**")
            protocol_lines = read_protocol_lines()
            if protocol_lines:
                st.code("\n".join(protocol_lines[-20:]), language="text")
            else:
                st.info("No protocol entries yet.")

    section_box(
        "6) Evidence Written",
        "Observability layer for the run",
        "trusted",
        evidence_content,
    )


def render_pending_approval() -> None:
    request = st.session_state.get("pending_approval_request")
    if not request:
        return

    st.markdown("## 🟡 Human Approval Required")
    st.warning("This action requires human approval before continuing.")

    def approval_request_content() -> None:
        show_kv("action", request.action)
        #show_kv("target", request.target)
        show_kv("content", request.content)
        show_kv("reason", request.reason)
        show_kv("risk_flags", request.risk_flags or [])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve", type="primary", use_container_width=True):
                st.session_state["approval_decision"] = True
                st.rerun()

        with col2:
            if st.button("Deny", use_container_width=True):
                st.session_state["approval_decision"] = False
                st.rerun()

    section_box(
        "Approval Request",
        "Human-in-the-loop checkpoint",
        "agent",
        approval_request_content,
    )


def run_workflow(customer_id: str) -> None:
    try:
        result = run_customer_strategy_workflow(
            customer_id,
            verbose=False,
            approval_handler=streamlit_approval_handler,
        )
        st.session_state["last_result"] = result
        st.session_state["pending_approval_request"] = None
        st.session_state["pending_customer_id"] = None

    except ApprovalPending as pending:
        st.session_state["pending_approval_request"] = pending.request
        st.session_state["pending_customer_id"] = customer_id


def init_session_state() -> None:
    defaults = {
        "last_result": None,
        "pending_approval_request": None,
        "pending_customer_id": None,
        "approval_decision": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    st.set_page_config(page_title="PyTexas MCP Demo", layout="wide")
    init_session_state()

    st.title("PyTexas MCP Secure Agent Demo")
    st.caption("Trusted tools + untrusted enrichment")

    with st.sidebar:
        st.header("Controls")
        customer_id = st.selectbox(
            "Scenario",
            options=["cust_email_demo", "cust_001", "cust_002", "cust_003"],
            index=0,
        )

        if st.button("Reset logs", use_container_width=True):
            reset_logs()
            st.session_state["last_result"] = None
            st.session_state["pending_approval_request"] = None
            st.session_state["pending_customer_id"] = None
            st.session_state["approval_decision"] = None
            st.success("Logs reset.")

        if st.button("Run scenario", type="primary", use_container_width=True):
            st.session_state["last_result"] = None
            st.session_state["pending_approval_request"] = None
            st.session_state["pending_customer_id"] = customer_id
            st.session_state["approval_decision"] = None
            run_workflow(customer_id)

        st.markdown("---")
        st.markdown("### Protocol Monitor")
        protocol_lines = read_protocol_lines()
        if protocol_lines:
            st.code("\n".join(protocol_lines[-20:]), language="text")
        else:
            st.caption("No protocol messages yet.")

    pending_customer_id = st.session_state.get("pending_customer_id")
    approval_decision = st.session_state.get("approval_decision")

    if pending_customer_id and approval_decision is not None:
        run_workflow(pending_customer_id)

    if st.session_state.get("pending_approval_request"):
        render_pending_approval()

    if st.session_state.get("last_result"):
        render_results(st.session_state["last_result"])
    elif not st.session_state.get("pending_approval_request"):
        st.info("Pick a scenario and click **Run scenario**.")


if __name__ == "__main__":
    main()
