# Delegation Patterns

How strategic agents delegate tactical tasks to specialized agents.

## Overview

Strategic agents handle high-level reasoning and planning. They delegate tactical execution to specialized agents for focused, repeatable tasks.

```
┌─────────────────────────────────────────────────────────────┐
│                    STRATEGIC AGENT                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Analyze  │→ │  Plan    │→ │ Execute  │→ │ Monitor  │    │
│  └──────────┘  └──────────┘  └────┬─────┘  └──────────┘    │
│                                    │                         │
│                    ┌───────────────┼───────────────┐        │
│                    ▼               ▼               ▼        │
│              ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│              │ Tactical │   │ Tactical │   │ Tactical │    │
│              │ Agent A  │   │ Agent B  │   │ Agent C  │    │
│              └──────────┘   └──────────┘   └──────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Delegation Registry

### incident-commander

**Delegates to:**
- `pattern-follower` - Apply fix patterns
- `documentation-writer` - Document incident and lessons learned

**Example Flow:**
```
1. Analyze incident severity and impact
2. Plan response strategy
3. Execute:
   - Direct: Diagnose and mitigate
   - Delegate: pattern-follower → Apply fix
   - Delegate: documentation-writer → Post-mortem
4. Monitor resolution
```

### security-auditor

**Delegates to:**
- `secret-scanner` - Find exposed credentials
- `vulnerability-scanner` - Check for CVEs
- `documentation-writer` - Security report

**Example Flow:**
```
1. Analyze security posture
2. Plan audit scope
3. Execute:
   - Delegate: secret-scanner → Scan for secrets
   - Delegate: vulnerability-scanner → Check dependencies
   - Direct: Review architecture
   - Delegate: documentation-writer → Security report
4. Monitor remediation
```

### code-reviewer

**Delegates to:**
- `linting-fixer` - Apply code formatting

**Example Flow:**
```
1. Analyze code changes
2. Plan review approach
3. Execute:
   - Direct: Architecture review
   - Delegate: linting-fixer → Fix style issues
   - Direct: Logic review
4. Compile feedback
```

### refactoring-specialist

**Delegates to:**
- `deduplication-engine` - Remove code duplication
- `pattern-follower` - Apply consistent patterns
- `test-generator` - Generate tests for refactored code

**Example Flow:**
```
1. Analyze code structure
2. Plan refactoring strategy
3. Execute:
   - Delegate: deduplication-engine → Remove duplicates
   - Delegate: pattern-follower → Apply patterns
   - Delegate: test-generator → Add test coverage
4. Verify behavior preserved
```

## Delegation Mechanisms

### Via Config.yaml

Strategic agents declare their delegation targets:

```yaml
# agents/incident-commander/config.yaml
name: incident-commander
tier: strategic
delegates_to:
  - pattern-follower
  - documentation-writer
```

### Via MCP Server

When executing a strategic agent:

```python
# Agent returns delegation targets in result
result = agent.run(context)
# result.delegations = ["pattern-follower", "documentation-writer"]
```

### Via Gemini CLI Chaining

```bash
# Strategic agent plans
./invoke-agent.sh security-auditor "Audit the auth module"
# Output includes: "Delegate to: secret-scanner, vulnerability-scanner"

# Execute tactical agents
./invoke-agent.sh secret-scanner "Scan auth module for secrets"
./invoke-agent.sh vulnerability-scanner "Check auth module dependencies"
```

## Delegation Best Practices

### 1. Keep Tactical Agents Focused

Each tactical agent should do ONE thing well:
- `commit-writer` → Only writes commit messages
- `linting-fixer` → Only fixes linting/formatting
- `secret-scanner` → Only scans for secrets

### 2. Strategic Agents Coordinate

Strategic agents should:
- Never implement tactical tasks directly
- Always delegate to specialized agents
- Coordinate and consolidate results
- Handle failures gracefully

### 3. Clear Handoff Protocol

When delegating:
1. Provide clear task description
2. Include relevant context
3. Specify expected output format
4. Handle delegation failures

### 4. Result Aggregation

Strategic agents should:
- Collect all tactical results
- Identify conflicts or issues
- Provide unified summary
- Recommend next steps

## Common Delegation Scenarios

### Security Audit

```
security-auditor
├── secret-scanner (find exposed credentials)
├── vulnerability-scanner (check for CVEs)
└── documentation-writer (generate report)
```

### Code Quality Review

```
code-reviewer
├── linting-fixer (fix style issues)
├── test-generator (suggest tests)
└── documentation-writer (review comments)
```

### Incident Response

```
incident-commander
├── ci-debugger (if CI-related)
├── pattern-follower (apply fix)
└── documentation-writer (post-mortem)
```

### Architecture Planning

```
architecture-designer
├── api-designer (API contracts)
├── documentation-writer (architecture docs)
└── test-generator (integration tests)
```

### Migration Planning

```
migration-specialist
├── dependency-analyzer (check compatibility)
├── pattern-follower (migration patterns)
└── documentation-writer (migration guide)
```

## Error Handling

### Delegation Failure

If a tactical agent fails:
1. Log the failure
2. Continue with remaining delegations
3. Report partial success
4. Suggest manual intervention if critical

### Missing Agent

If delegated agent doesn't exist:
1. Log warning
2. Skip delegation
3. Note in result
4. Continue with available agents

## Extending Delegation

### Adding New Tactical Agent

1. Create agent in `agents/` directory
2. Add to strategic agent's `delegates_to` list
3. Test delegation workflow

### Creating New Strategic Agent

1. Create agent with clear delegation targets
2. Define delegation protocol in AGENT.md
3. Add `delegates_to` to config.yaml
4. Document delegation scenarios
