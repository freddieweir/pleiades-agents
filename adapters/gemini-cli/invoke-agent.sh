#!/bin/bash
#
# Invoke a Pleiades agent via Gemini CLI
#
# Usage:
#   ./invoke-agent.sh <agent-name> [task description]
#   ./invoke-agent.sh incident-commander "Production API returning 500 errors"
#
# The agent's AGENT.md is passed to Gemini CLI as a prompt file.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENTS_DIR="$REPO_ROOT/agents"

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <agent-name> [task description]"
    echo ""
    echo "Available agents:"
    ls -1 "$AGENTS_DIR" | sed 's/^/  /'
    exit 1
fi

AGENT_NAME="$1"
shift
TASK_DESCRIPTION="${*:-}"

AGENT_DIR="$AGENTS_DIR/$AGENT_NAME"
AGENT_MD="$AGENT_DIR/AGENT.md"
CONFIG_YAML="$AGENT_DIR/config.yaml"

# Validate agent exists
if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent '$AGENT_NAME' not found"
    echo ""
    echo "Available agents:"
    ls -1 "$AGENTS_DIR" | sed 's/^/  /'
    exit 1
fi

if [ ! -f "$AGENT_MD" ]; then
    echo "Error: AGENT.md not found for '$AGENT_NAME'"
    exit 1
fi

# Build the prompt
PROMPT=""

if [ -n "$TASK_DESCRIPTION" ]; then
    PROMPT="Task: $TASK_DESCRIPTION

Please follow the instructions below to complete this task.

"
fi

# Invoke Gemini CLI with agent instructions
# Using -p @file.md format as specified
echo "Invoking agent: $AGENT_NAME"
echo "---"

if [ -n "$TASK_DESCRIPTION" ]; then
    # Pass task description and agent instructions
    echo "$PROMPT" | gemini -p @"$AGENT_MD"
else
    # Just load agent instructions interactively
    gemini -p @"$AGENT_MD"
fi
