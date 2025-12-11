#!/usr/bin/env python3
"""Migrate Floor Guardian agents to unified agent format."""

import ast
import re
import yaml
from pathlib import Path

# Source and target directories
GUARDIANS_DIR = Path("/Users/fweir/git/internal/repos/nazarick-floor-guardians/src/floor_guardians/agents")
AGENTS_DIR = Path("/Users/fweir/git/internal/repos/pleiades-agents/agents")

# Skip these files
SKIP_FILES = {"__init__.py", "template.py"}


def parse_python_class(file_path: Path) -> dict | None:
    """Parse Python file and extract class attributes."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except SyntaxError:
        return None

    # Find the class that inherits from BaseFloorGuardian
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Check if it's a Floor Guardian class
        bases = [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]
        if "BaseFloorGuardian" not in bases:
            continue

        result = {
            "class_name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "name": None,
            "expertise": [],
            "requires_opus": True,
            "description": "",
            "delegates_to": [],
        }

        # Extract class attributes
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    name = target.id
                    value = item.value

                    if name == "name" and isinstance(value, ast.Constant):
                        result["name"] = value.value
                    elif name == "expertise" and isinstance(value, ast.List):
                        result["expertise"] = [
                            elt.value for elt in value.elts if isinstance(elt, ast.Constant)
                        ]
                    elif name == "requires_opus" and isinstance(value, ast.Constant):
                        result["requires_opus"] = value.value
                    elif name == "description" and isinstance(value, ast.Constant):
                        result["description"] = value.value

        # Extract delegate_to references from source
        delegates = set()
        for match in re.findall(r'"delegate_to":\s*"([^"]+)"', content):
            delegates.add(match)
        for match in re.findall(r"'delegate_to':\s*'([^']+)'", content):
            delegates.add(match)
        for match in re.findall(r'delegate_to_skill\(\s*skill_name=["\']([^"\']+)["\']', content):
            delegates.add(match)
        result["delegates_to"] = sorted(delegates)

        return result

    return None


def categorize_agent(name: str) -> str:
    """Determine agent category based on name."""
    categories = {
        "crisis": ["incident"],
        "security": ["security", "opsec", "git-history"],
        "development": ["code-reviewer", "refactoring", "pattern"],
        "architecture": ["architect", "api-designer", "integration"],
        "operations": ["infrastructure", "ci-", "automation", "monitoring"],
        "performance": ["performance", "dependency-analyzer"],
        "planning": ["planner", "migration", "documentation-strategist", "testing-strategist", "tech-debt"],
    }

    for category, keywords in categories.items():
        if any(kw in name for kw in keywords):
            return category

    return "development"


def generate_agent_md(info: dict) -> str:
    """Generate AGENT.md content from parsed info."""
    name = info["name"] or "unknown"
    display_name = name.replace("-", " ").title()
    desc = info["description"] or info["docstring"].split("\n")[0] if info["docstring"] else display_name
    docstring = info["docstring"]
    delegates = info["delegates_to"]

    delegation_section = ""
    if delegates:
        delegate_list = "\n".join(f"- {d}" for d in delegates)
        delegation_section = f"""
## Delegation

This agent can delegate tactical tasks to:
{delegate_list}
"""

    return f"""# {display_name}

{desc}

## Purpose

{docstring if docstring else f"Strategic agent for {display_name.lower()} tasks."}

## Execution Pattern

This is a strategic agent following the four-phase execution model:

### 1. Analyze
- Assess the situation and gather context
- Identify constraints, requirements, and risks
- Determine complexity and scope

### 2. Plan
- Develop a multi-step strategy
- Identify opportunities to delegate tactical tasks
- Define success criteria for each step

### 3. Execute
- Coordinate implementation of the plan
- Delegate tactical tasks to specialized agents
- Handle errors and adapt as needed

### 4. Monitor
- Track progress and verify outcomes
- Adapt strategy if circumstances change
- Document results and lessons learned
{delegation_section}
## Activation

This agent activates when prompts contain keywords related to:
{chr(10).join(f"- {kw}" for kw in info["expertise"][:5])}

## Guidelines

- Prioritize thorough analysis before action
- Break complex problems into manageable steps
- Delegate tactical execution to specialized agents
- Document decisions and reasoning
- Verify outcomes against success criteria
"""


def generate_config(info: dict) -> dict:
    """Generate config.yaml from parsed info."""
    name = info["name"]

    config = {
        "name": name,
        "description": info["description"],
        "version": "1.0.0",
        "status": "stable",
        "tier": "strategic",
        "category": categorize_agent(name),
        "requires_opus": info["requires_opus"],
        "triggers": {
            "keywords": info["expertise"],
        },
        "runtime": {
            "mode": "on-demand",
            "preferred": "mcp",
            "fallback": "gemini-cli",
        },
    }

    if info["delegates_to"]:
        config["delegates_to"] = info["delegates_to"]

    return config


def migrate_guardian(file_path: Path) -> None:
    """Migrate a single Floor Guardian to unified format."""
    info = parse_python_class(file_path)
    if not info or not info["name"]:
        print(f"  [SKIP] Could not parse {file_path.name}")
        return

    name = info["name"]

    # Create target directory
    target_dir = AGENTS_DIR / name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Write config.yaml
    config = generate_config(info)
    config_path = target_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Write AGENT.md
    agent_md = generate_agent_md(info)
    agent_path = target_dir / "AGENT.md"
    agent_path.write_text(agent_md)

    delegates = f" → {', '.join(info['delegates_to'])}" if info["delegates_to"] else ""
    print(f"  [OK] {name}{delegates}")


def main():
    print("Migrating Floor Guardian agents to unified format...\n")

    agent_files = sorted([
        f for f in GUARDIANS_DIR.glob("*.py")
        if f.name not in SKIP_FILES
    ])
    print(f"Found {len(agent_files)} agents to migrate:\n")

    for agent_file in agent_files:
        migrate_guardian(agent_file)

    print(f"\nMigration complete! Check {AGENTS_DIR} for results.")


if __name__ == "__main__":
    main()
