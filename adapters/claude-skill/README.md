# Claude Skill Adapter

Generates Claude Code's `.claude/skills/` structure from unified agents.

## Overview

This adapter converts agents with `runtime.mode: preload` (tactical agents) into Claude Code's native skill format for automatic keyword activation.

## Usage

```bash
# Generate skills
uv run python adapters/claude-skill/generate-skills.py

# Or via the provided script
./adapters/claude-skill/generate-skills.py
```

## What Gets Generated

Only agents with `runtime.mode: preload` in their `config.yaml` are converted to Claude skills. This typically includes tactical agents designed for keyword activation.

### Input (agents/{name}/)

```yaml
# config.yaml
name: commit-writer
description: Generate conventional commit messages
triggers:
  keywords: ["commit message", "git commit"]
runtime:
  mode: preload  # ← This triggers skill generation
```

```markdown
# AGENT.md
Instructions for the agent...
```

### Output (.claude/skills/{name}/)

```markdown
---
name: commit-writer
description: Generate conventional commit messages
keywords: ["commit message", "git commit"]
activation: keywords
---

Instructions for the agent...
```

## Selective Generation

Only `preload` mode agents become Claude skills:

| Agent | Runtime Mode | Generated as Skill? |
|-------|--------------|---------------------|
| commit-writer | preload | Yes |
| linting-fixer | preload | Yes |
| incident-commander | on-demand | No |
| security-auditor | on-demand | No |

Strategic agents (`on-demand` mode) are intended to be invoked explicitly via MCP or Gemini CLI, not preloaded as skills.

## Integration

After generating skills, Claude Code will automatically activate them when prompts contain matching keywords.

```
# Example prompt triggering commit-writer
User: "Write a commit message for these changes"
# → commit-writer skill activates automatically
```
