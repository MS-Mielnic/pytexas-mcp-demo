#!/bin/bash

# Resolve project root (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export PYTHONPATH="$PROJECT_ROOT"

echo "Starting MCP inspector for Untrusted Demo FastMCP..."
echo "Using python: $(which python)"
echo "PYTHONPATH: $PYTHONPATH"

mcp-inspector "$(which python)" -m servers.untrusted_demo_server.server
