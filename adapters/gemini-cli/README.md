# Gemini CLI Adapter

Invoke Pleiades agents via Google's Gemini CLI.

## Overview

This adapter wraps agents for invocation via Gemini CLI using the `gemini -p @file.md` format. It's designed for on-demand agent execution where you explicitly choose which agent to run.

## Prerequisites

- Gemini CLI installed and configured
- API key set up for Gemini

## Usage

### Basic Usage

```bash
# List available agents
./adapters/gemini-cli/invoke-agent.sh

# Invoke agent with task
./adapters/gemini-cli/invoke-agent.sh incident-commander "Production API returning 500 errors"

# Interactive mode (no task description)
./adapters/gemini-cli/invoke-agent.sh code-reviewer
```

### From Repo Root

```bash
./adapters/gemini-cli/invoke-agent.sh commit-writer "Write commit for auth changes"
```

## How It Works

1. Script locates the agent's `AGENT.md` file
2. Passes it to Gemini CLI via `gemini -p @agents/{name}/AGENT.md`
3. If task description provided, prepends it to the prompt

## Agent Selection

Unlike the MCP server which uses keyword matching, the Gemini CLI adapter requires explicit agent selection. This is intentional for on-demand use cases where you know which agent you need.

For automatic agent selection, use the MCP server's `select_pleiades_agent` tool.

## Examples

### Incident Response

```bash
./invoke-agent.sh incident-commander "Database connection timeouts increasing"
```

### Code Review

```bash
./invoke-agent.sh code-reviewer "Review the authentication module changes"
```

### Generate Commit Message

```bash
./invoke-agent.sh commit-writer "Write commit for the new API endpoints"
```

## Integration with Orchestrator

The orchestrator can use this adapter to delegate tasks to Gemini:

```python
import subprocess

def invoke_gemini_agent(agent_name: str, task: str) -> str:
    result = subprocess.run(
        ["./adapters/gemini-cli/invoke-agent.sh", agent_name, task],
        capture_output=True,
        text=True,
        cwd="/path/to/pleiades-agents"
    )
    return result.stdout
```
