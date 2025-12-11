#!/usr/bin/env python3
"""Validate all agents have correct structure and configuration."""

import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# Required fields in config.yaml
REQUIRED_FIELDS = {"name", "description", "tier", "triggers"}
VALID_TIERS = {"strategic", "tactical"}
VALID_MODES = {"on-demand", "preload"}
VALID_STATUS = {"stable", "draft"}
VALID_RUNTIMES = {"claude-native", "gemini-cli", "mcp", "claude-api"}


def validate_agent(agent_dir: Path) -> list[str]:
    """Validate a single agent directory."""
    errors = []
    agent_name = agent_dir.name

    config_path = agent_dir / "config.yaml"
    agent_path = agent_dir / "AGENT.md"

    # Check config.yaml exists
    if not config_path.exists():
        errors.append(f"{agent_name}: Missing config.yaml")
        return errors

    # Parse config.yaml
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"{agent_name}: Invalid YAML in config.yaml: {e}")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(f"{agent_name}: Missing required field '{field}'")

    # Validate name matches directory
    if config.get("name") != agent_name:
        errors.append(f"{agent_name}: name '{config.get('name')}' doesn't match directory")

    # Validate tier
    tier = config.get("tier")
    if tier and tier not in VALID_TIERS:
        errors.append(f"{agent_name}: Invalid tier '{tier}' (must be: {VALID_TIERS})")

    # Validate runtime structure (v2 schema)
    runtime = config.get("runtime", {})

    # Check mode
    mode = runtime.get("mode")
    if mode and mode not in VALID_MODES:
        errors.append(f"{agent_name}: Invalid runtime mode '{mode}' (must be: {VALID_MODES})")

    # Check discovery field (v2 schema)
    discovery = runtime.get("discovery")
    if discovery:
        if discovery not in VALID_RUNTIMES:
            errors.append(f"{agent_name}: Invalid discovery runtime '{discovery}' (must be: {VALID_RUNTIMES})")

    # Check execution field (v2 schema)
    execution = runtime.get("execution", {})
    if execution:
        preferred = execution.get("preferred")
        if preferred and preferred not in VALID_RUNTIMES:
            errors.append(f"{agent_name}: Invalid execution.preferred '{preferred}' (must be: {VALID_RUNTIMES})")

        fallbacks = execution.get("fallbacks", [])
        if fallbacks:
            if not isinstance(fallbacks, list):
                errors.append(f"{agent_name}: execution.fallbacks must be a list")
            else:
                for fb in fallbacks:
                    if fb not in VALID_RUNTIMES:
                        errors.append(f"{agent_name}: Invalid fallback runtime '{fb}' (must be: {VALID_RUNTIMES})")

    # Warn if using old schema (preferred/fallback at runtime level)
    if "preferred" in runtime and "execution" not in runtime:
        errors.append(f"{agent_name}: [WARN] Using old schema format (runtime.preferred). Consider migrating to v2 schema (runtime.execution.preferred)")
    if "fallback" in runtime and "execution" not in runtime:
        errors.append(f"{agent_name}: [WARN] Using old schema format (runtime.fallback). Consider migrating to v2 schema (runtime.execution.fallbacks)")

    # Validate status
    status = config.get("status")
    if status and status not in VALID_STATUS:
        errors.append(f"{agent_name}: Invalid status '{status}' (must be: {VALID_STATUS})")

    # Validate keywords
    triggers = config.get("triggers", {})
    keywords = triggers.get("keywords", [])
    if not keywords:
        errors.append(f"{agent_name}: No keywords defined in triggers")
    elif not isinstance(keywords, list):
        errors.append(f"{agent_name}: keywords must be a list")

    # Check AGENT.md exists (warning, not error)
    if not agent_path.exists():
        errors.append(f"{agent_name}: [WARN] Missing AGENT.md")

    return errors


def main():
    print("Validating Pleiades Agents...\n")

    if not AGENTS_DIR.exists():
        print(f"Error: Agents directory not found: {AGENTS_DIR}")
        sys.exit(1)

    agent_dirs = sorted([d for d in AGENTS_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(agent_dirs)} agents to validate\n")

    all_errors = []
    valid_count = 0
    warning_count = 0

    strategic_count = 0
    tactical_count = 0
    v2_schema_count = 0

    for agent_dir in agent_dirs:
        errors = validate_agent(agent_dir)
        warnings = [e for e in errors if "[WARN]" in e]
        real_errors = [e for e in errors if "[WARN]" not in e]

        if real_errors:
            for error in real_errors:
                print(f"  [ERROR] {error}")
            all_errors.extend(real_errors)
        elif warnings:
            print(f"  [WARN]  {agent_dir.name}")
            warning_count += 1
        else:
            print(f"  [OK]    {agent_dir.name}")
            valid_count += 1

        # Count tiers and schema versions
        config_path = agent_dir / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if config.get("tier") == "strategic":
                    strategic_count += 1
                else:
                    tactical_count += 1

                # Check for v2 schema
                runtime = config.get("runtime", {})
                if "execution" in runtime:
                    v2_schema_count += 1

    print(f"\n{'=' * 50}")
    print(f"Summary:")
    print(f"  Total agents: {len(agent_dirs)}")
    print(f"  Valid: {valid_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Errors: {len(all_errors)}")
    print(f"")
    print(f"  Strategic: {strategic_count}")
    print(f"  Tactical: {tactical_count}")
    print(f"  Schema v2: {v2_schema_count}/{len(agent_dirs)}")

    if all_errors:
        print(f"\nValidation FAILED with {len(all_errors)} errors")
        sys.exit(1)
    else:
        print(f"\nValidation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
