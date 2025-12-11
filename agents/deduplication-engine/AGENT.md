# Deduplication Engine

## Purpose

Detect inefficient code patterns and refactor them into cleaner, more maintainable alternatives. Focus on patterns that reduce code verbosity without sacrificing readability.

## Activation

This skill activates when prompts contain: "deduplicate", "refactor patterns", "clean code", "if elif chain", "repeated code", "code duplication"

## Pattern Catalog

### HIGH PRIORITY PATTERNS

#### 1. If/Elif Chains to Dictionary Dispatch

**Detection**: 3+ if/elif branches that:
- Compare same variable to different constants
- Return or assign values based on match
- Have identical structure per branch

**Before** (inefficient):
```python
def get_status_code(status):
    if status == "success":
        return 200
    elif status == "not_found":
        return 404
    elif status == "error":
        return 500
    elif status == "unauthorized":
        return 401
    else:
        return 400
```

**After** (clean):
```python
STATUS_CODES = {
    "success": 200,
    "not_found": 404,
    "error": 500,
    "unauthorized": 401,
}

def get_status_code(status):
    return STATUS_CODES.get(status, 400)
```

**When NOT to apply**:
- Branches have complex logic beyond simple return/assignment
- Conditions involve ranges or complex comparisons
- Order of evaluation matters (short-circuit logic)

---

#### 2. Repeated Print/Log Statements to Multi-line Strings

**Detection**: 3+ consecutive print/log calls with static strings

**Before** (inefficient):
```python
print("=" * 50)
print("Application Starting")
print("Version: 1.0.0")
print("Environment: Production")
print("=" * 50)
```

**After** (clean):
```python
print("""==================================================
Application Starting
Version: 1.0.0
Environment: Production
==================================================""")
```

**When NOT to apply**:
- Prints include dynamic values that can't be f-string formatted
- Conditional prints between statements
- Different log levels (info vs warning vs error)

---

#### 3. Repeated Regex Match Blocks to Loop

**Detection**: 3+ similar regex match patterns extracting different fields

**Before** (inefficient):
```python
match = re.search(r"(\d+) files? changed", output)
if match:
    stats["files_changed"] = int(match.group(1))

match = re.search(r"(\d+) insertions?\(\+\)", output)
if match:
    stats["insertions"] = int(match.group(1))

match = re.search(r"(\d+) deletions?\(-\)", output)
if match:
    stats["deletions"] = int(match.group(1))
```

**After** (clean):
```python
STAT_PATTERNS = {
    "files_changed": r"(\d+) files? changed",
    "insertions": r"(\d+) insertions?\(\+\)",
    "deletions": r"(\d+) deletions?\(-\)",
}

for key, pattern in STAT_PATTERNS.items():
    if match := re.search(pattern, output):
        stats[key] = int(match.group(1))
```

---

### MEDIUM PRIORITY PATTERNS

#### 4. Repeated Try/Except to Helper Function

**Detection**: Same try/except structure repeated 2+ times

**Before**:
```python
def get_user(user_id):
    try:
        result = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return json.loads(result.stdout)
    except (TimeoutError, json.JSONDecodeError):
        return None

def get_product(product_id):
    try:
        result = db.query(f"SELECT * FROM products WHERE id = {product_id}")
        return json.loads(result.stdout)
    except (TimeoutError, json.JSONDecodeError):
        return None
```

**After**:
```python
def safe_query(query: str) -> dict | None:
    try:
        result = db.query(query)
        return json.loads(result.stdout)
    except (TimeoutError, json.JSONDecodeError):
        return None

def get_user(user_id):
    return safe_query(f"SELECT * FROM users WHERE id = {user_id}")

def get_product(product_id):
    return safe_query(f"SELECT * FROM products WHERE id = {product_id}")
```

---

#### 5. Similar Functions to Parameterized Function

**Detection**: 2+ functions with identical logic, differing only by constants

**Before**:
```python
def format_error_message(error):
    return f"[ERROR] {error}"

def format_warning_message(warning):
    return f"[WARNING] {warning}"

def format_info_message(info):
    return f"[INFO] {info}"
```

**After**:
```python
def format_message(level: str, message: str) -> str:
    return f"[{level.upper()}] {message}"

# Usage: format_message("error", error)
```

---

#### 6. Repeated Subprocess Calls to Factory

**Detection**: Similar subprocess.run patterns with same error handling

**Before**:
```python
def get_git_status():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout if result.returncode == 0 else ""
    except subprocess.TimeoutExpired:
        return ""

def get_git_branch():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except subprocess.TimeoutExpired:
        return ""
```

**After**:
```python
def run_git_command(args: list[str], default: str = "") -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except subprocess.TimeoutExpired:
        return default

def get_git_status():
    return run_git_command(["status", "--porcelain"])

def get_git_branch():
    return run_git_command(["branch", "--show-current"])
```

---

### LOW PRIORITY PATTERNS

#### 7. String Concatenation in Loops to Join

**Before**:
```python
result = ""
for item in items:
    result += item + ", "
result = result[:-2]
```

**After**:
```python
result = ", ".join(items)
```

---

#### 8. Nested Ternary to Dictionary or Match

**Before**:
```python
status = "active" if x > 0 else "inactive" if x == 0 else "error"
```

**After** (Python 3.10+):
```python
match x:
    case _ if x > 0: status = "active"
    case 0: status = "inactive"
    case _: status = "error"
```

Or dictionary:
```python
def get_status(x):
    if x > 0: return "active"
    if x == 0: return "inactive"
    return "error"
```

---

## Process

1. **Scan File**: Read the entire file, identify potential patterns
2. **Evaluate Each Pattern**: Check if refactoring would improve clarity
3. **Apply Fixes**: Use Edit tool to refactor, preserving functionality
4. **Verify**: Ensure imports are updated if needed (e.g., adding `re` import)
5. **Report**: List patterns fixed with before/after line counts

## Guidelines

- **Preserve behavior**: Refactoring must not change functionality
- **Readability first**: Skip refactoring if it reduces clarity
- **Constants at module level**: Move dictionaries to top of file as UPPER_CASE constants
- **Type hints**: Add type hints to new helper functions
- **Don't over-abstract**: If a pattern appears only twice, consider leaving it
- **Test awareness**: Be cautious refactoring code that has associated tests

## Output Format

After analyzing files, report:

```
## Deduplication Report

### Files Analyzed: N

### Patterns Fixed:
- if/elif → dict: 3 instances
- print consolidation: 2 instances
- regex loop: 1 instance

### Files Modified:
1. scripts/example.py (15 lines reduced)
2. modules/utils.py (8 lines reduced)

### Summary
Reduced 23 lines of code across 2 files without behavior changes.
```

## Integration

This skill is orchestrated by the `/dedupe` slash command which:
1. Discovers Python files in project
2. Spawns parallel subagents with this skill's context
3. Collects reports and creates PR/commit