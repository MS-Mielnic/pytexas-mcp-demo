from shared.audit import write_protocol_log


def log_middleware_event(event_type: str, detail: str) -> None:
    write_protocol_log(f"{event_type} | implementation=fastmcp | {detail}")
