#!/usr/bin/env python3
"""Generate Claude Code .claude/skills/ structure from unified agents.

This adapter converts agents with runtime.mode: preload into Claude Code's
native skill format for automatic keyword activation.
"""

import yaml
import shutil
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
OUTPUT_DIR = REPO_ROOT / ".claude" / "skills"


def should_generate_skill(config: dict) -> bool:
    """Check if agent should be generated as a Claude skill."""
    # Only generate for preload mode (tactical agents)
    runtime = config.get("runtime", {})
    mode = runtime.get("mode", "on-demand")
    return mode == "preload"


def generate_skill_md(config: dict, agent_md: str) -> str:
    """Generate Claude Code SKILL.md format with YAML frontmatter."""
    # Build frontmatter
    frontmatter = {
        "name": config["name"],
        "description": config["description"],
        "keywords": config.get("triggers", {}).get("keywords", []),
        "activation": "keywords",
    }

    # Add model hint if requires_opus
    if config.get("requires_opus"):
        frontmatter["model"] = "opus-4"

    # Generate YAML frontmatter
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

    # Combine frontmatter and content
    return f"---\n{yaml_str}---\n\n{agent_md}"


def generate_skill(agent_dir: Path) -> bool:
    """Generate a Claude skill from an agent directory."""
    config_path = agent_dir / "config.yaml"
    agent_path = agent_dir / "AGENT.md"

    if not config_path.exists():
        return False

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Check if this should be a skill
    if not should_generate_skill(config):
        return False

    # Load agent instructions
    agent_md = ""
    if agent_path.exists():
        agent_md = agent_path.read_text()

    # Generate skill content
    skill_content = generate_skill_md(config, agent_md)

    # Create output directory
    skill_dir = OUTPUT_DIR / config["name"]
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(skill_content)

    return True


def main():
    print("Generating Claude Code skills from unified agents...\n")

    # Clean existing skills
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Process all agents
    generated = 0
    skipped = 0

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue

        if generate_skill(agent_dir):
            print(f"  [OK] {agent_dir.name}")
            generated += 1
        else:
            print(f"  [SKIP] {agent_dir.name} (on-demand mode)")
            skipped += 1

    print(f"\nGenerated {generated} skills, skipped {skipped} on-demand agents")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
