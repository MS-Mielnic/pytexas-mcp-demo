#Logging
import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

from shared.config import ensure_runtime_dirs, settings


def new_request_id() -> str:
    return str(uuid4())


def get_audit_log_path() -> Path:
    ensure_runtime_dirs()
    return settings.audit_log_dir / "audit.jsonl"


def write_audit_event(
    *,
    tool_name: str,
    arguments: dict,
    sanitized_arguments: dict,
    policy_decision: str,
    result_status: str,
    error_message: str | None = None,
    request_id: str | None = None,
    latency_ms: float | None = None,
    event_type: str | None = None,
    implementation: str | None = None,
    execution_context: dict | None = None,
    provenance: dict | None = None,
) -> dict:
    event = {
        "request_id": request_id or new_request_id(),
        "tool_name": tool_name,
        "timestamp": datetime.now(UTC).isoformat(),
        "arguments": arguments,
        "sanitized_arguments": sanitized_arguments,
        "execution_context": execution_context,
        "provenance": provenance,
        "policy_decision": policy_decision,
        "result_status": result_status,
        "error_message": error_message,
        "latency_ms": latency_ms,
        "event_type": event_type,
        "implementation": implementation,
    }

    log_path = get_audit_log_path()
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    return event


def write_protocol_log(message: str) -> None:
    ensure_runtime_dirs()
    log_path = settings.protocol_log_dir / "protocol.log"
    timestamp = datetime.now(UTC).isoformat()

    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {message}\n")
