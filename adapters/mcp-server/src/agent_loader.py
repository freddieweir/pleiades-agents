"""Dynamic agent loader for unified agent format."""

import logging
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context information for agent execution."""

    task_description: str
    repository_path: Optional[str] = None
    environment: Optional[str] = None
    severity: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Result from agent execution."""

    status: str
    message: str
    analysis: Optional[Dict[str, Any]] = None
    plan: Optional[List[Dict[str, Any]]] = None
    execution_details: Optional[Dict[str, Any]] = None
    monitoring_data: Optional[Dict[str, Any]] = None
    delegations: Optional[List[str]] = None


class Agent:
    """
    Dynamic agent loaded from AGENT.md and config.yaml.

    This replaces the Python class-based Floor Guardian approach
    with a configuration-driven approach.
    """

    def __init__(
        self,
        name: str,
        description: str,
        tier: str,
        category: str,
        keywords: List[str],
        requires_opus: bool = False,
        delegates_to: Optional[List[str]] = None,
        runtime_mode: str = "on-demand",
        instructions: str = "",
    ):
        self.name = name
        self.description = description
        self.tier = tier
        self.category = category
        self.keywords = keywords
        self.requires_opus = requires_opus
        self.delegates_to = delegates_to or []
        self.runtime_mode = runtime_mode
        self.instructions = instructions
        self.logger = logging.getLogger(f"pleiades.{name}")

    def can_handle(self, task_description: str) -> bool:
        """Check if this agent can handle the given task."""
        task_lower = task_description.lower()
        return any(keyword.lower() in task_lower for keyword in self.keywords)

    def get_match_score(self, task_description: str) -> int:
        """Get the number of matching keywords."""
        task_lower = task_description.lower()
        return sum(1 for kw in self.keywords if kw.lower() in task_lower)

    def get_matched_keywords(self, task_description: str) -> List[str]:
        """Get list of matched keywords."""
        task_lower = task_description.lower()
        return [kw for kw in self.keywords if kw.lower() in task_lower]

    def run(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent.

        For instruction-based agents, this returns a structured result
        with the agent instructions and metadata.
        """
        self.logger.info(f"Running agent: {self.name}")

        # Build analysis based on agent metadata
        analysis = {
            "agent": self.name,
            "tier": self.tier,
            "category": self.category,
            "task": context.task_description,
            "matched_keywords": self.get_matched_keywords(context.task_description),
            "severity": context.severity,
            "environment": context.environment,
        }

        # Build plan (for strategic agents)
        plan = []
        if self.tier == "strategic":
            plan = [
                {"step": 1, "action": "Analyze task", "delegate_to": None},
                {"step": 2, "action": "Develop strategy", "delegate_to": None},
                {"step": 3, "action": "Execute plan", "delegate_to": None},
                {"step": 4, "action": "Verify results", "delegate_to": None},
            ]
            # Add delegation steps if configured
            for i, delegate in enumerate(self.delegates_to, start=5):
                plan.append({
                    "step": i,
                    "action": f"Delegate tactical task to {delegate}",
                    "delegate_to": delegate,
                })

        return AgentResult(
            status="ready",
            message=f"Agent {self.name} ready for task execution",
            analysis=analysis,
            plan=plan if plan else None,
            delegations=self.delegates_to if self.delegates_to else None,
        )


class AgentLoader:
    """
    Loads agents dynamically from the agents/ directory.

    Each agent must have:
    - config.yaml: Agent metadata and configuration
    - AGENT.md: Agent instructions
    """

    def __init__(self, agents_dir: Optional[Path] = None):
        """Initialize the agent loader."""
        if agents_dir is None:
            # Default to agents/ relative to repo root
            agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
        self.agents_dir = agents_dir
        self._agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger("pleiades.loader")
        self._load_agents()

    def _load_agents(self):
        """Load all agents from the agents directory."""
        if not self.agents_dir.exists():
            self.logger.warning(f"Agents directory not found: {self.agents_dir}")
            return

        for agent_dir in sorted(self.agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            config_path = agent_dir / "config.yaml"
            agent_path = agent_dir / "AGENT.md"

            if not config_path.exists():
                self.logger.debug(f"Skipping {agent_dir.name}: no config.yaml")
                continue

            try:
                agent = self._load_agent(config_path, agent_path)
                if agent:
                    self._agents[agent.name] = agent
            except Exception as e:
                self.logger.error(f"Failed to load agent {agent_dir.name}: {e}")

        self.logger.info(f"Loaded {len(self._agents)} agents")

    def _load_agent(self, config_path: Path, agent_path: Path) -> Optional[Agent]:
        """Load a single agent from config and instructions."""
        with open(config_path) as f:
            config = yaml.safe_load(f)

        instructions = ""
        if agent_path.exists():
            instructions = agent_path.read_text()

        # Extract keywords from triggers
        keywords = config.get("triggers", {}).get("keywords", [])

        # Extract runtime mode
        runtime = config.get("runtime", {})
        runtime_mode = runtime.get("mode", "on-demand")

        return Agent(
            name=config.get("name", config_path.parent.name),
            description=config.get("description", ""),
            tier=config.get("tier", "tactical"),
            category=config.get("category", "development"),
            keywords=keywords,
            requires_opus=config.get("requires_opus", False),
            delegates_to=config.get("delegates_to", []),
            runtime_mode=runtime_mode,
            instructions=instructions,
        )

    def select_agent(
        self,
        task_description: str,
        explicit_agent: Optional[str] = None,
    ) -> Optional[Agent]:
        """Select the best agent for a task."""
        # Priority 1: Explicit selection
        if explicit_agent:
            agent = self._agents.get(explicit_agent)
            if agent:
                self.logger.info(f"Selected explicit agent: {explicit_agent}")
                return agent
            self.logger.warning(f"Requested agent not found: {explicit_agent}")

        # Priority 2: Keyword matching
        matches = []
        for agent in self._agents.values():
            score = agent.get_match_score(task_description)
            if score > 0:
                matches.append((score, agent))

        if matches:
            # Sort by score descending
            matches.sort(key=lambda x: x[0], reverse=True)
            best_agent = matches[0][1]
            self.logger.info(
                f"Selected agent by keyword match: {best_agent.name} "
                f"(score: {matches[0][0]})"
            )
            return best_agent

        self.logger.warning("No suitable agent found")
        return None

    def list_agents(self) -> List[str]:
        """Get list of all agent names."""
        return sorted(self._agents.keys())

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get a specific agent by name."""
        return self._agents.get(name)

    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent."""
        agent = self._agents.get(name)
        if not agent:
            return None

        return {
            "name": agent.name,
            "description": agent.description,
            "tier": agent.tier,
            "category": agent.category,
            "keywords": agent.keywords,
            "requires_opus": agent.requires_opus,
            "delegates_to": agent.delegates_to,
            "runtime_mode": agent.runtime_mode,
        }

    def get_agents_by_tier(self, tier: str) -> List[Agent]:
        """Get all agents of a specific tier."""
        return [a for a in self._agents.values() if a.tier == tier]

    def get_agents_by_category(self, category: str) -> List[Agent]:
        """Get all agents in a specific category."""
        return [a for a in self._agents.values() if a.category == category]
