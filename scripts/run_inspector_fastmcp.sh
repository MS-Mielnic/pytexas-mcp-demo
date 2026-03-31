#!/bin/bash

echo "Starting MCP inspector for FastMCP..."
echo "Using python: $(which python)"

mcp-inspector "$(which python)" -m servers.fastmcp_server.server
