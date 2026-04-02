# Using MCP to create secure, observable and governed ai applications.

This project demonstrates how to build **AI systems that can take actions safely and with full auditability** using the Model Context Protocol (MCP) in Python.

It shows how an AI application can use **validation, policy, and approval controls** to rule interactions between agens, and MCP servers.

---

## Key Idea

**Same protocol. Different permissions. Enforced at every boundary.**

- MCP standardizes access to tools
- But **standardized access does not imply equal authority**
- Every component enforces its own constraints

---

## MCP and FastMCP

- **Model Context Protocol (MCP)** is the protocol used to structure how components in this system interact with tools exposed by MCP servers

In this architecture:
- MCP servers expose tools (e.g. send email, update customer strategy)
- The agent communicates with these servers using MCP
- Both trusted and untrusted servers follow the same protocol

- **FastMCP** is used to implement these servers in Python

It wraps the underlying MCP protocol so you don’t have to:
- implement the protocol handshake
- manage message passing over stdio
- manually structure JSON requests and responses

Instead, we define tools and middleware directly in Python, while still conforming to MCP.

---

## What This Demo Shows

This project is focused on **controlling what is allowed to happen when tools are used by an agent to perform actions on systems**.

The system is designed so that:

- Untrusted external systems provide **data to enrich a customers database**
- Agent can **use MCP server's tools, reason, and recommend next action**
- Trusted MCP server enforce **what actions are actually allowed**
- Sensitive actions require **explicit approval**

---

## How to run it

```bash
python run_demo.py

or 

streamlit run streamlit_app/app.py
