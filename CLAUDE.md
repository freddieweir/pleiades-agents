# CLAUDE.md

Development guidance for the pleiades-agents repository.

## Repository Overview

Unified AI agent architecture consolidating strategic agents (Floor Guardians) and tactical agents (Pleiades Skills) into a single source of truth.

**Key Concept**: Skills ARE agents. The only difference is runtime mode:
- `preload` = loaded into context upfront (Claude skill behavior)
- `on-demand` = invoked when needed (Gemini CLI / MCP behavior)

## Architecture

```
pleiades-agents/
├── agents/                    # 43 unified agents
│   └── {name}/
│       ├── AGENT.md           # Universal instructions
│       └── config.yaml        # Metadata & runtime config
│
├── orchestrator/              # Routing and coordination
│   ├── routing.md             # Decision tree
│   └── delegation-patterns.md # Strategic→tactical patterns
│
├── adapters/                  # Runtime integrations
│   ├── claude-skill/          # Generate .claude/skills/
│   ├── gemini-cli/            # CLI wrapper
│   └── mcp-server/            # MCP server (Floor Guardians)
│
├── lib/                       # Shared utilities
│   ├── agent_loader.py        # Load AGENT.md + config.yaml
│   └── keyword_matcher.py     # Routing logic
│
└── tests/
    └── validate_agents.py     # Agent validation
```

## Agent Design

### AGENT.md Format

```markdown
# Agent Name

Brief description of what this agent does.

## Purpose
One paragraph explaining the agent's role.

## Activation
Keywords that trigger this agent:
- keyword 1
- keyword 2

## Process
1. Step one
2. Step two
3. Step three

## Output Format
What the agent produces.

## Examples
Concrete usage examples.

## Guidelines
- Do this
- Don't do that
```

### config.yaml Schema

```yaml
name: agent-name              # kebab-case, matches directory
description: Brief one-liner
version: 1.0.0
status: stable | draft        # draft = template/incomplete

tier: strategic | tactical    # strategic = analyze→plan→execute→monitor
category: security | development | operations | planning | git | ...
requires_opus: false          # needs advanced reasoning?

triggers:
  keywords:
    - "keyword 1"
    - "keyword 2"

runtime:
  mode: on-demand | preload   # on-demand = agent, preload = skill
  preferred: gemini-cli | claude-native | mcp
  fallback: claude-api

delegates_to:                 # strategic agents only
  - pattern-follower
  - commit-writer
```

## Common Commands

```bash
# Validate all agents
uv run python tests/validate_agents.py

# Generate Claude skills
uv run python adapters/claude-skill/generate-skills.py

# Run MCP server
uv run python -m adapters.mcp_server

# Invoke via Gemini CLI
./adapters/gemini-cli/invoke-agent.sh {agent-name} "task"
```

## Adding New Agents

1. Create directory: `mkdir agents/{agent-name}`
2. Write AGENT.md with instructions
3. Create config.yaml:
   ```yaml
   name: agent-name
   description: What it does
   version: 1.0.0
   status: stable
   tier: tactical
   category: development
   triggers:
     keywords: ["trigger1", "trigger2"]
   runtime:
     mode: preload
     preferred: claude-native
   ```
4. Run validation: `uv run python tests/validate_agents.py`
5. Regenerate skills if tactical: `uv run python adapters/claude-skill/generate-skills.py`

## Strategic vs Tactical

### Strategic Agents (tier: strategic)
- Four-phase execution: analyze → plan → execute → monitor
- Delegate tactical tasks to other agents
- Require more reasoning (often `requires_opus: true`)
- Examples: incident-commander, security-auditor, project-planner

### Tactical Agents (tier: tactical)
- Single-purpose execution
- Fast, focused, repeatable
- Usually `mode: preload` for skill behavior
- Examples: commit-writer, linting-fixer, test-generator

## Git Standards

- Conventional commits: `type(scope): description`
- No AI attribution markers
- Keep commits focused and atomic

## OPSEC

- `.md` files in `/agents/` are committed (public agent definitions)
- Never commit API keys or credentials
- Use 1Password CLI for secrets
