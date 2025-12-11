#!/usr/bin/env python3
"""Migrate Pleiades Squad skills to unified agent format."""

import re
import yaml
from pathlib import Path

# Source and target directories
SKILLS_DIR = Path("/Users/fweir/git/internal/repos/nazarick-pleiades-squad/.claude/skills")
AGENTS_DIR = Path("/Users/fweir/git/internal/repos/pleiades-agents/agents")

# Skills known to be fully developed
STABLE_SKILLS = {
    "commit-writer",
    "deduplication-engine",
    "tech-debt-scanner",
    "writing-style-analyzer",
}


def parse_skill_file(skill_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and content from skill file."""
    content = skill_path.read_text()

    # Split frontmatter from content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            markdown = parts[2].strip()
            return frontmatter, markdown

    return {}, content


def convert_to_config(frontmatter: dict, skill_name: str) -> dict:
    """Convert skill frontmatter to unified config.yaml format."""
    keywords = frontmatter.get("keywords", [])

    return {
        "name": skill_name,
        "description": frontmatter.get("description", f"{skill_name} skill"),
        "version": "1.0.0",
        "status": "stable" if skill_name in STABLE_SKILLS else "draft",
        "tier": "tactical",
        "category": categorize_skill(skill_name),
        "requires_opus": False,
        "triggers": {
            "keywords": keywords if isinstance(keywords, list) else [keywords],
        },
        "runtime": {
            "mode": "preload",
            "preferred": "claude-native",
            "fallback": "gemini-cli",
        },
    }


def categorize_skill(name: str) -> str:
    """Determine skill category based on name."""
    categories = {
        "git": ["commit", "branch", "merge", "pr-", "changelog"],
        "security": ["secret", "vulnerability", "opsec"],
        "code-quality": ["lint", "style", "deduplic", "tech-debt"],
        "testing": ["test"],
        "documentation": ["doc", "api-doc", "writing-style"],
        "infrastructure": ["docker", "config", "env-"],
        "dependencies": ["dependency"],
        "compliance": ["license"],
        "data": ["metadata"],
    }

    for category, keywords in categories.items():
        if any(kw in name for kw in keywords):
            return category

    return "development"


def migrate_skill(skill_dir: Path) -> None:
    """Migrate a single skill to unified format."""
    skill_name = skill_dir.name

    # Find skill file (case-insensitive)
    skill_files = list(skill_dir.glob("*.md"))
    if not skill_files:
        print(f"  [SKIP] No .md file in {skill_name}")
        return

    skill_file = skill_files[0]

    # Parse skill
    frontmatter, markdown = parse_skill_file(skill_file)

    # Create target directory
    target_dir = AGENTS_DIR / skill_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Write config.yaml
    config = convert_to_config(frontmatter, skill_name)
    config_path = target_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Write AGENT.md (markdown content without frontmatter)
    agent_path = target_dir / "AGENT.md"
    agent_path.write_text(markdown)

    status = config["status"]
    print(f"  [OK] {skill_name} ({status})")


def main():
    print("Migrating Pleiades Squad skills to unified format...\n")

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(skill_dirs)} skills to migrate:\n")

    for skill_dir in skill_dirs:
        migrate_skill(skill_dir)

    print(f"\nMigration complete! {len(skill_dirs)} skills migrated to {AGENTS_DIR}")


if __name__ == "__main__":
    main()
