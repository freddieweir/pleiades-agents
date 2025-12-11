# Agent Routing

Decision tree and guidelines for selecting the appropriate Pleiades agent.

## Routing Overview

```
┌─────────────────────────────────────────────────────┐
│                    USER REQUEST                      │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              EXPLICIT AGENT REQUESTED?               │
│                                                      │
│  "Use incident-commander for this"                   │
│  "Run the code-reviewer agent"                       │
└────────────────┬────────────────┬───────────────────┘
                Yes               No
                 │                 │
                 ▼                 ▼
         ┌──────────────┐  ┌─────────────────────────┐
         │ Use explicit │  │   KEYWORD MATCHING      │
         │    agent     │  │                         │
         └──────────────┘  │ Scan request for agent  │
                           │ trigger keywords        │
                           └───────────┬─────────────┘
                                       │
                           ┌───────────┴───────────┐
                           │                       │
                      Match found           No match
                           │                       │
                           ▼                       ▼
                   ┌───────────────┐      ┌───────────────┐
                   │ Select agent  │      │ Ask user to   │
                   │ with highest  │      │ clarify or    │
                   │ keyword score │      │ choose agent  │
                   └───────────────┘      └───────────────┘
```

## Keyword-Based Routing

### Priority 1: Crisis/Incident

| Keywords | Agent | Tier |
|----------|-------|------|
| incident, emergency, outage, production down | `incident-commander` | Strategic |
| error response, incident response | `incident-responder` | Strategic |

### Priority 2: Security

| Keywords | Agent | Tier |
|----------|-------|------|
| security audit, vulnerability, threat model | `security-auditor` | Strategic |
| opsec, sanitize, sensitive data | `opsec-sanitizer` | Strategic |
| secret scan, credentials, exposed secrets | `secret-scanner` | Tactical |
| vulnerability scan, CVE | `vulnerability-scanner` | Tactical |
| rewrite history, amend, squash | `git-history-rewriter` | Strategic |

### Priority 3: Development

| Keywords | Agent | Tier |
|----------|-------|------|
| code review, pr review, quality check | `code-reviewer` | Strategic |
| refactor, cleanup, duplicate | `refactoring-specialist` | Strategic |
| pattern, consistent, template | `pattern-follower` | Tactical |
| lint, format code, auto-fix | `linting-fixer` | Tactical |
| deduplicate, repeated code | `deduplication-engine` | Tactical |

### Priority 4: Testing

| Keywords | Agent | Tier |
|----------|-------|------|
| test strategy, coverage | `testing-strategist` | Strategic |
| generate tests, unit tests | `test-generator` | Tactical |

### Priority 5: Architecture

| Keywords | Agent | Tier |
|----------|-------|------|
| architecture, design, microservices | `architecture-designer` | Strategic |
| api, endpoint, rest, graphql | `api-designer` | Strategic |
| integration, orchestrate, pipeline | `integration-orchestrator` | Strategic |

### Priority 6: Operations

| Keywords | Agent | Tier |
|----------|-------|------|
| infrastructure, deployment review | `infrastructure-auditor` | Strategic |
| ci, pipeline, github actions | `ci-debugger` | Strategic |
| automation, workflow | `automation-architect` | Strategic |
| monitoring, observability, metrics | `monitoring-designer` | Strategic |

### Priority 7: Performance

| Keywords | Agent | Tier |
|----------|-------|------|
| performance, slow, latency, optimize | `performance-optimizer` | Strategic |
| dependency, dependencies, version | `dependency-analyzer` | Strategic |

### Priority 8: Planning

| Keywords | Agent | Tier |
|----------|-------|------|
| plan, requirements, strategy | `project-planner` | Strategic |
| migrate, upgrade, modernize | `migration-specialist` | Strategic |
| documentation strategy, docs strategy | `documentation-strategist` | Strategic |
| tech debt, abandoned code | `tech-debt-analyst` | Strategic |
| tech debt scan, unused code | `tech-debt-scanner` | Tactical |

### Priority 9: Git Operations

| Keywords | Agent | Tier |
|----------|-------|------|
| commit message, git commit | `commit-writer` | Tactical |
| review pr, pull request | `pr-reviewer` | Tactical |
| branch naming, branch lifecycle | `branch-manager` | Tactical |
| merge conflict, resolution | `merge-coordinator` | Tactical |
| changelog, release notes | `changelog-generator` | Tactical |

### Priority 10: Documentation

| Keywords | Agent | Tier |
|----------|-------|------|
| api documentation, api docs | `api-documenter` | Tactical |
| generate docs, technical documentation | `documentation-writer` | Tactical |
| writing style | `writing-style-analyzer` | Tactical |
| code style | `style-enforcer` | Tactical |

### Priority 11: Infrastructure

| Keywords | Agent | Tier |
|----------|-------|------|
| docker compose, compose file | `docker-composer` | Tactical |
| generate config, configuration | `config-generator` | Tactical |
| env validation, environment | `env-validator` | Tactical |

### Priority 12: Other

| Keywords | Agent | Tier |
|----------|-------|------|
| dependency update, package update | `dependency-updater` | Tactical |
| license, compliance | `license-checker` | Tactical |
| extract metadata, structured data | `metadata-extractor` | Tactical |

## Strategic vs Tactical Selection

### When to Use Strategic Agents

Use strategic agents when the task:
- Requires analysis before action
- Involves multiple steps or phases
- Needs coordination across systems
- Benefits from planning and monitoring
- May require delegation to tactical agents

**Example**: "We have a security issue in the authentication module"
→ Use `security-auditor` (strategic) which may delegate to `secret-scanner` and `vulnerability-scanner` (tactical)

### When to Use Tactical Agents

Use tactical agents when the task:
- Is well-defined and focused
- Has a clear, repeatable pattern
- Produces a specific output
- Can be completed quickly
- Doesn't require planning

**Example**: "Write a commit message for these changes"
→ Use `commit-writer` (tactical) directly

## Multi-Agent Scenarios

### Complex Task Decomposition

For complex tasks, the orchestrator may:

1. **Start with strategic agent** for analysis and planning
2. **Delegate tactical steps** to specialized agents
3. **Coordinate results** back to strategic agent
4. **Monitor and adapt** if needed

```
User: "Review and improve the API security"
                    │
                    ▼
        ┌───────────────────────┐
        │   security-auditor    │ ← Strategic
        │   (analyze & plan)    │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌────────┐   ┌────────────┐   ┌────────────┐
│ secret │   │vulnerability│   │   code    │
│scanner │   │  scanner   │   │ reviewer  │
└────────┘   └────────────┘   └────────────┘
    │               │               │
    └───────────────┼───────────────┘
                    ▼
        ┌───────────────────────┐
        │   security-auditor    │
        │  (consolidate results)│
        └───────────────────────┘
```

## Scoring Algorithm

When multiple agents match keywords:

1. Count matching keywords per agent
2. Weight by keyword specificity (longer phrases score higher)
3. Consider tier preference (strategic for complex, tactical for focused)
4. Select highest scoring agent

```python
def select_agent(task_description: str) -> Agent:
    scores = []
    for agent in all_agents:
        score = 0
        for keyword in agent.keywords:
            if keyword.lower() in task_description.lower():
                score += len(keyword.split())  # Multi-word phrases score higher
        if score > 0:
            scores.append((score, agent))

    return max(scores, key=lambda x: x[0])[1] if scores else None
```

## Runtime Selection

### Claude (Preload/Skill Mode)

- Tactical agents automatically activate via keywords
- No explicit selection needed
- Generated via `generate-skills.py`

### Gemini CLI (On-Demand Mode)

- Explicit agent selection required
- Use `invoke-agent.sh <agent-name> "task"`
- Best for strategic agents

### MCP Server

- Both automatic and explicit selection
- `select_pleiades_agent` for keyword-based routing
- `execute_pleiades_agent` for explicit selection

## Fallback Strategy

When no agent matches:

1. **Ask for clarification**: "Could you specify what type of task this is?"
2. **Suggest options**: "This could be handled by X, Y, or Z. Which fits best?"
3. **Default to project-planner**: For general planning and strategy tasks
