# Pleiades Agents

Unified AI agent architecture serving both Claude (skills/preload) and Gemini CLI (on-demand agents).

## Overview

This repository consolidates two agent systems into a single, universal format:

- **Strategic Agents** (21) - High-level reasoning, planning, and coordination
- **Tactical Agents** (22) - Focused, repeatable task execution

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                         │
│                                                         │
│        ┌────────────────────────────────────┐           │
│        │      pleiades-agents (unified)     │           │
│        │                                    │           │
│        │  /agents                           │           │
│        │    ├── incident-commander/         │           │
│        │    ├── code-reviewer/              │           │
│        │    ├── commit-writer/              │           │
│        │    └── .../                        │           │
│        │                                    │           │
│        │  config.yaml determines:           │           │
│        │    • preload (skill) vs on-demand  │           │
│        │    • claude vs gemini runtime      │           │
│        └─────────────┬──────────────────────┘           │
│                      │                                  │
│         ┌────────────┴────────────┐                     │
│         ▼                         ▼                     │
│   ┌──────────┐              ┌──────────┐                │
│   │  Claude  │              │  Gemini  │                │
│   │ (preload │              │   CLI    │                │
│   │  skills) │              │(on-demand│                │
│   └──────────┘              └──────────┘                │
│                                                         │
│            ✓ Single source of truth                     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Using with Claude Code (Skills)

Generate Claude skills from agents:

```bash
uv run python adapters/claude-skill/generate-skills.py
```

This creates `.claude/skills/` directory with all tactical agents configured for preload.

### Using with Gemini CLI

Invoke any agent directly:

```bash
./adapters/gemini-cli/invoke-agent.sh commit-writer "Write a commit message for these changes"
```

### Using MCP Server

Start the MCP server for Claude Desktop integration:

```bash
uv run python -m adapters.mcp_server
```

## Agent Structure

Each agent follows a universal format:

```
agents/{agent-name}/
├── AGENT.md        # Instructions (works as skill OR agent prompt)
└── config.yaml     # Metadata, triggers, runtime preferences
```

### Config Schema

```yaml
name: agent-name
description: Brief one-liner
version: 1.0.0
status: stable | draft

tier: strategic | tactical
category: security | development | operations | planning | git
requires_opus: false

triggers:
  keywords:
    - "keyword 1"
    - "keyword 2"

runtime:
  mode: on-demand | preload    # on-demand = agent, preload = skill
  preferred: gemini-cli | claude-native | mcp
  fallback: claude-api

delegates_to:                  # For strategic agents
  - pattern-follower
  - commit-writer
```

## Agent Categories

### Strategic Agents (21)

High-level reasoning agents that analyze, plan, execute, and monitor:

| Agent | Category | Description |
|-------|----------|-------------|
| incident-commander | crisis | Emergency response coordination |
| security-auditor | security | Comprehensive security analysis |
| code-reviewer | development | Deep code analysis and QA |
| architecture-designer | architecture | System architecture design |
| project-planner | planning | Project planning and requirements |

[See full list in `agents/`]

### Tactical Agents (22)

Focused agents that execute specific, repeatable tasks:

| Agent | Category | Description |
|-------|----------|-------------|
| commit-writer | git | Generate conventional commit messages |
| linting-fixer | code-quality | Apply linting and formatting fixes |
| test-generator | testing | Generate test cases from code |
| secret-scanner | security | Scan for exposed credentials |

[See full list in `agents/`]

## Adapters

### Claude Skill Adapter

Converts `AGENT.md` files into Claude Code's `.claude/skills/` format for automatic keyword activation.

```bash
uv run python adapters/claude-skill/generate-skills.py
```

### Gemini CLI Adapter

Wraps agents for invocation via Gemini CLI:

```bash
./adapters/gemini-cli/invoke-agent.sh {agent-name} "task description"
```

### MCP Server

Preserves Floor Guardian functionality for Claude Desktop integration. Exposes tools:
- `select_floor_guardian` - Route to appropriate agent
- `execute_floor_guardian` - Run agent with full context
- `list_floor_guardians` - List available agents
- `get_floor_guardian_info` - Get agent details

## Development

### Prerequisites

- Python 3.11+
- uv package manager

### Setup

```bash
uv sync
```

### Validating Agents

```bash
uv run python tests/validate_agents.py
```

### Adding a New Agent

1. Create directory: `agents/{agent-name}/`
2. Write `AGENT.md` with instructions
3. Create `config.yaml` with metadata
4. Run validation: `uv run python tests/validate_agents.py`

## License

MIT
