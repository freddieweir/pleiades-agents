# Agent Configuration Schema v2

This document defines the config.yaml structure for all agents in the pleiades-agents repository.

## config.yaml Structure

```yaml
name: agent-name              # kebab-case, must match directory name
description: Brief one-liner  # Displayed in agent listings
version: 1.0.0                # Semantic version
status: stable | draft        # stable = production-ready, draft = template

tier: strategic | tactical    # Determines execution pattern
category: security | development | operations | planning | git | crisis | ...
requires_opus: false          # true if agent needs advanced reasoning

triggers:
  keywords:                   # Keywords that activate this agent
    - "keyword 1"
    - "keyword 2"

runtime:
  mode: on-demand | preload   # preload = Skill behavior, on-demand = invoke when needed
  discovery: claude-native    # How orchestrator discovers agent capabilities
  execution:
    preferred: gemini-cli     # Primary execution runtime
    fallbacks:
      - mcp                   # Fallback options in priority order
      - claude-api

delegates_to:                 # Optional: agents this one delegates to (strategic only)
  - pattern-follower
  - commit-writer
```

## Runtime Options

| Runtime | Model Lock-in | Description |
|---------|---------------|-------------|
| `claude-native` | Claude only | Claude Code Skills - loaded into context for discovery/routing |
| `gemini-cli` | Gemini only | Gemini CLI via `invoke-agent.sh` - 1M token context window |
| `mcp` | **Any model** | Model Context Protocol - works with Ollama, OpenAI, Claude via MCP clients |
| `claude-api` | Claude only | Direct Claude API calls |

## Schema Fields

### Required Fields

- `name`: Must match the directory name (kebab-case)
- `description`: Brief description for agent listings
- `tier`: Either `strategic` or `tactical`
- `triggers.keywords`: List of keywords that activate this agent

### Optional Fields

- `version`: Semantic version (default: 1.0.0)
- `status`: `stable` or `draft` (default: stable)
- `category`: Agent category for organization
- `requires_opus`: Boolean, true if agent needs Opus-level reasoning
- `runtime`: Runtime configuration (see below)
- `delegates_to`: List of agents this one delegates work to

## Runtime Configuration

### Discovery vs Execution

The schema v2 separates **discovery** from **execution**:

- **Discovery**: How the orchestrator learns about agent capabilities. All agents use `claude-native` so they're loaded as Skills for routing decisions.

- **Execution**: How the agent actually runs when invoked. This varies by agent tier:
  - Tactical: `claude-native` (quick, inline execution)
  - Strategic: `gemini-cli` (delegate heavy work to Gemini's 1M context)

### Tactical Agent Runtime

```yaml
runtime:
  mode: preload
  discovery: claude-native
  execution:
    preferred: claude-native    # Quick, inline execution
    fallbacks:
      - gemini-cli              # Delegate if context needed
      - mcp                     # Open-WebUI, LM Studio
```

### Strategic Agent Runtime

```yaml
runtime:
  mode: on-demand
  discovery: claude-native
  execution:
    preferred: gemini-cli       # Delegate heavy work
    fallbacks:
      - mcp                     # Model-agnostic fallback
      - claude-api              # Direct Claude if needed
```

## Tier Differences

### Strategic Agents

- Follow 4-phase execution: analyze → plan → execute → monitor
- May delegate to tactical agents via `delegates_to`
- Typically `requires_opus: true` for complex reasoning
- Default execution: `gemini-cli` for cost/context optimization

### Tactical Agents

- Single-purpose, focused execution
- Fast and repeatable
- Default execution: `claude-native` for inline use
- Typically `requires_opus: false`

## Validation

Run the validation script to check all agents:

```bash
uv run python tests/validate_agents.py
```

The validator checks:
- Required fields present
- Name matches directory
- Valid tier, mode, and status values
- Keywords defined
- AGENT.md exists
- v2 schema structure (discovery + execution)

## Examples

### Minimal Tactical Agent

```yaml
name: commit-writer
description: Generate professional conventional commit messages
tier: tactical
triggers:
  keywords:
    - commit message
    - git commit
runtime:
  mode: preload
  discovery: claude-native
  execution:
    preferred: claude-native
    fallbacks:
      - gemini-cli
      - mcp
```

### Full Strategic Agent

```yaml
name: incident-commander
description: Emergency response coordination and crisis management
version: 1.0.0
status: stable
tier: strategic
category: crisis
requires_opus: true
triggers:
  keywords:
    - incident
    - emergency
    - crisis
    - outage
runtime:
  mode: on-demand
  discovery: claude-native
  execution:
    preferred: gemini-cli
    fallbacks:
      - mcp
      - claude-api
delegates_to:
  - documentation-writer
  - pattern-follower
```
