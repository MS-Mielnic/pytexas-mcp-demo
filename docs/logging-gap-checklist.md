# Logging Gap Checklist

## Point 7 target
Design the logging and audit format up front so the demo shows not only actions, but also observability and control.

## Already implemented

### Audit log
- [x] request_id
- [x] timestamp
- [x] tool_name
- [x] arguments
- [x] sanitized_arguments
- [x] policy_decision
- [x] result_status
- [x] error_message
- [x] latency_ms per tool call
- [x] event_type field
- [x] implementation field (`raw` or `fastmcp`)

### Protocol log
- [x] server start
- [x] server interrupt
- [x] server stop
- [x] raw request/response boundary logging
- [x] FastMCP middleware request/response logging

### FastMCP-specific observability
- [x] middleware-level request logging
- [x] middleware-level response logging
- [x] middleware-level exception logging 

## Still missing

### Protocol / transport layer
- [x] connection/open event
- [x] session/close event
- [x] tool call boundary event at protocol layer

## Recommended implementation order
1. Demonstrate middleware-level exception logging
2. Add protocol/transport event touch logging
3. Review whether raw and FastMCP protocol logs should share a more unified event vocabulary
