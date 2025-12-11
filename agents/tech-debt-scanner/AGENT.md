# Tech Debt Scanner

## Purpose

Detect code and features that exist but don't actually work. Focus on finding false confidence issues - services that appear operational but are silently failing or disabled.

## Activation

This skill activates when prompts contain: "tech debt", "abandoned code", "unused", "broken config", "dead code", "stale"

## Detection Patterns

### 🔴 CRITICAL - False Sense of Security

#### 1. Services Running But Non-Functional

**Pattern**: Docker service is UP but misconfigured to do nothing.

**Detection**:
```yaml
# Alertmanager null receiver pattern
receivers:
- name: 'null'
  # Discards all alerts silently
```

**What to look for**:
- Receivers named `null`, `blackhole`, `devnull`
- Handlers that immediately return without action
- Middleware that passes through without processing
- Webhooks pointing to non-existent endpoints

**Example from carian-observatory**:
```
File: services/monitoring/alertmanager/alertmanager.yml
Issue: All alerts route to null receiver
Impact: Monitoring appears active but no alerts are ever sent
```

---

#### 2. Missing Generated Config Files

**Pattern**: Template file exists but generated output doesn't.

**Detection**:
```bash
# For each *.template file, check if non-template version exists
find . -name "*.template" | while read template; do
    generated="${template%.template}"
    if [ ! -f "$generated" ]; then
        echo "MISSING: $generated (template: $template)"
    fi
done
```

**Common causes**:
- Build/deploy script not run
- Template generation in Makefile not invoked
- CI/CD pipeline skipped template step
- File accidentally deleted

**Example from carian-observatory**:
```
Template: prometheus/alerts.yml.template
Expected: prometheus/alerts.yml
Actual: prometheus/alerts.yml is a DIRECTORY (broken)
Impact: Prometheus has no alert rules loaded
```

---

### 🟡 MEDIUM - Technical Debt

#### 3. Disabled-By-Default Features

**Pattern**: Code exists but is commented out or disabled.

**Detection in docker-compose.yml**:
```yaml
include:
  # - path: services/feature/docker-compose.yml  # DISABLED
  - path: services/other/docker-compose.yml
```

**Detection in code**:
```python
FEATURE_ENABLED = False  # TODO: enable when ready
# FEATURE_ENABLED = True
```

**What to look for**:
- Commented `include:` statements in docker-compose
- Feature flags permanently set to `false`
- Services with `profiles:` that are never activated
- `if False:` or `if 0:` code blocks

---

#### 4. Stale Code Markers

**Pattern**: TODO/FIXME comments that have aged out.

**Detection**:
```python
# TODO: implement this (2024-03-15)  # Over 30 days old
# FIXME: memory leak here
# HACK: workaround for bug #123
# XXX: temporary solution
```

**Age thresholds**:
- 30 days: Warning
- 60 days: Concern
- 90 days: Likely abandoned

**Git-based detection**:
```bash
# Find files not modified in 60+ days
git log --format=%H --since="60 days ago" -- . | head -1
# If empty, file is stale
```

---

#### 5. Empty Implementations

**Pattern**: Functions/classes defined but not implemented.

**Detection**:
```python
def process_data(data):
    pass  # Empty body

def handle_event(event):
    raise NotImplementedError()  # Never implemented

class FeatureHandler:
    """Coming soon."""
    pass
```

---

### 🔵 LOW - Cleanup Candidates

#### 6. Obsolete Migration Scripts

**Pattern**: One-time scripts that remain after migration.

**Detection**:
- Scripts in `migrations/`, `scripts/migration/`
- Files with names like `migrate-*.sh`, `port-*.py`
- Comments mentioning specific migration dates

**Example**:
```
Path: scripts/migration/
Files: migrate-v1-to-v2.sh, portfolio-migration.sh
Last modified: 60+ days ago
Action: Archive or delete after verifying migration complete
```

---

#### 7. Backup Artifacts

**Pattern**: Backup copies that should be cleaned up.

**Detection**:
- Directories: `.backup/`, `.old/`, `_backup/`
- Files: `*.bak`, `*.old`, `*.backup`, `*_BACKUP_*`
- Git merge artifacts: `*.orig`

---

#### 8. Unused Dependencies

**Pattern**: Packages installed but never imported.

**Detection**:
```bash
# Python: packages in requirements.txt not imported
pip-check  # Or manual grep of imports

# Node: packages in package.json not required
npx depcheck
```

---

## Process

1. **Inventory Phase**
   - List all docker-compose services
   - Find all template files
   - Scan for code markers (TODO, FIXME, etc.)

2. **Health Check Phase**
   - For each service, verify config exists
   - Check for null/noop patterns in configs
   - Validate template→generated file pairs

3. **Staleness Analysis**
   - Git log analysis for file ages
   - Identify directories with no recent commits
   - Find code markers older than threshold

4. **Report Generation**
   - Group by severity (CRITICAL > MEDIUM > LOW)
   - Include file paths and line numbers
   - Provide specific remediation actions

## Output Format

```markdown
## Tech Debt Report: {repo-name}

**Scan Date**: {date}
**Files Scanned**: {count}
**Issues Found**: {critical}/{medium}/{low}

### 🔴 CRITICAL ({count})

#### 1. {component} - {issue}
- **File**: `{path}:{line}`
- **Impact**: {what's broken}
- **Fix**: {remediation}

### 🟡 MEDIUM ({count})

#### 1. {feature} - {status}
- **Last Modified**: {date}
- **Action**: {recommendation}

### 🔵 LOW ({count})

#### 1. {artifact} - {reason}
- **Path**: `{directory}`
- **Action**: Archive or delete

---

**Summary**: {brief overview of findings and recommended priority}
```

## Guidelines

- **Don't flag intentional disabling**: If there's a comment explaining why something is disabled, note it but don't mark as critical
- **Check git blame**: Recent changes might indicate active work, not abandonment
- **Consider context**: Migration scripts are obsolete by design after migration
- **Verify before recommending deletion**: Some "unused" code is for edge cases
- **Prioritize false security issues**: A broken alertmanager is worse than stale docs

## Integration

This skill is invoked by the `/tech-debt` slash command.

Can also be triggered by:
- Floor Guardian: `tech-debt-patrol`
- MCP: `mcp__floor-guardians__execute_floor_guardian` with agent `tech-debt-patrol`