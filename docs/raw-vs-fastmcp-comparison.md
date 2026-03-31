# Raw MCP vs FastMCP Comparison

## Goal
This repo demonstrates the same customer/order demo implemented in two ways:
- a raw MCP server in Python
- a FastMCP server in Python

Both implementations reuse the same application logic for:
- customer reads
- email policy enforcement
- sanitization
- audit logging

---

## What stays the same

Both servers use the same shared code for:
- `shared/services/customers.py`
- `shared/services/email.py`
- `shared/policy.py`
- `shared/sanitize.py`
- `shared/audit.py`
The business logic is the same.
The server implementation and the developer experience are different.

---

## Raw MCP server

### What is implemented manually
- stdin/stdout server loop
- JSON request parsing
- initialize handling
- tool listing
- tool dispatch
- response formatting
- error formatting

### Benefits
- makes protocol mechanics visible
- useful for visualizing trust boundaries and request flow
- shows where validation, routing, and enforcement happen

### Tradeoffs
- more boilerplate
- easier to make protocol mistakes
- Inspector integration requires more care
- response shaping is fully manual

---

## FastMCP server

### What the framework provides automatically
- tool registration
- schema generation
- better Inspector compatibility
- structured output support
- more MCP-native developer experience- the framework knows exactly what the protocol requests

### Benefits
- much less boilerplate
- cleaner integration with Inspector
- better schema visibility
- structured responses feel more natural in the UI

### Tradeoffs
- less visibility into protocol plumbing
- framework does not solve by itself the  need for policy and audit logic
- framework convenience does not provide security coverage

---

## Security and observability

FastMCP still needs::
- sanitization
- policy enforcement
- audit logging
- backend control logic

These controls still live in application code.

In this repo, both implementations (mcp raw and fastmcp)  rely on the same shared control layer.

---

## Demo behaviors

### Customer found
- returns sanitized customer data
- sensitive field `ssn_last4` is masked

### Customer not found
- returns a not found response

### Allowed email
- internal recipient succeeds

### Blocked email
- external recipient is denied
- sensitive content is denied

### Audit trail
- both allowed and blocked actions are logged to `logs/audit/audit.jsonl`

---

## Talking points for the presentation

### Raw MCP
“This version is useful for understanding what MCP servers are actually doing under the hood.”

### FastMCP
“This version gives us improved  developer experience with much less code.”

### Key takeaway
“FastMCP reduces protocol boilerplate, but the real controls still belong to us:
policy, sanitization, and audit logging.”

---

## Practical conclusion

Use raw MCP when:
- teaching the protocol
- exploring low-level behavior
- demonstrating where boundaries exist

Use FastMCP when:
- building faster
- integrating with Inspector and tooling
- you want cleaner server development with the same control logic
