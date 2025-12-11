# Pleiades Agents MCP Server

MCP (Model Context Protocol) server that exposes Pleiades Agents as tools for Claude Code integration.

## Overview

This adapter dynamically loads agents from the `agents/` directory and exposes them via MCP tools. Unlike the original Floor Guardians implementation that used Python classes, this version loads agent metadata from `config.yaml` files.

## Running the Server

### Direct (stdio mode)

```bash
# From repo root
uv run python -m adapters.mcp_server.src

# Or from this directory
cd adapters/mcp-server
uv run python -m src
```

### With mcpo proxy (REST API)

```bash
uvx mcpo --port 8000 -- uv run python -m adapters.mcp_server.src
```

## Claude Desktop Configuration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pleiades-agents": {
      "command": "uv",
      "args": ["run", "python", "-m", "adapters.mcp_server.src"],
      "cwd": "/path/to/pleiades-agents"
    }
  }
}
```

## Available Tools

### select_pleiades_agent

Select the most appropriate agent for a task based on keywords.

**Parameters:**
- `task_description` (required): Description of the task
- `explicit_agent`: Explicitly request a specific agent
- `severity`: low, medium, high, critical
- `environment`: vm, main, production, development

### execute_pleiades_agent

Execute an agent to analyze and plan a task.

**Parameters:**
- `agent_name` (required): Name of the agent
- `task_description` (required): Task description
- `repository_path`: Path to repository
- `severity`: Task severity
- `environment`: Environment context

### list_pleiades_agents

List all available agents with optional filtering.

**Parameters:**
- `tier`: Filter by strategic or tactical
- `category`: Filter by category

### get_pleiades_agent_info

Get detailed information about a specific agent.

**Parameters:**
- `agent_name` (required): Name of the agent

### get_agent_instructions

Get the full AGENT.md instructions for an agent.

**Parameters:**
- `agent_name` (required): Name of the agent

## Architecture

```
adapters/mcp-server/
├── src/
│   ├── __init__.py
│   ├── __main__.py        # Entry point
│   ├── agent_loader.py    # Dynamic agent loading from config.yaml
│   └── mcp_server.py      # MCP server and tool definitions
└── README.md
```

## Agent Loading

Agents are loaded dynamically from the `agents/` directory:

1. Each agent directory must contain:
   - `config.yaml`: Agent metadata and configuration
   - `AGENT.md`: Agent instructions (optional but recommended)

2. The `AgentLoader` class parses config.yaml and creates `Agent` instances.

3. Agent selection uses keyword matching from the `triggers.keywords` field.

## Differences from Floor Guardians

| Feature | Floor Guardians | Pleiades Agents MCP |
|---------|-----------------|---------------------|
| Agent Definition | Python classes | config.yaml + AGENT.md |
| Registration | Manual imports | Dynamic loading |
| Execution | Full 4-phase | Metadata + instructions |
| Extensibility | Add Python file | Add directory with YAML |

## Testing

```bash
# Test with MCP inspector
npx @modelcontextprotocol/inspector uv run python -m adapters.mcp_server.src
```
