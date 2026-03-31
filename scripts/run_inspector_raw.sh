#!/bin/bash

echo "Starting MCP inspector..."
echo "Using python: $(which python)"

mcp-inspector "$(which python)" -m servers.raw_mcp.server
