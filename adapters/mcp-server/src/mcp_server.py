"""MCP server exposing Pleiades Agents as tools for Claude Code integration."""

import logging
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .agent_loader import AgentLoader, AgentContext

logger = logging.getLogger(__name__)

# Create MCP server
mcp_server = Server("pleiades-agents")

# Global agent loader instance
agent_loader = AgentLoader()


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Pleiades Agent tools."""
    tools = [
        Tool(
            name="select_pleiades_agent",
            description="Select the most appropriate Pleiades agent for a task based on keywords and context",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to be performed"
                    },
                    "explicit_agent": {
                        "type": "string",
                        "description": "Optional: Explicitly request a specific agent by name"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Severity level for the task"
                    },
                    "environment": {
                        "type": "string",
                        "enum": ["vm", "main", "production", "development"],
                        "description": "Environment context"
                    }
                },
                "required": ["task_description"]
            }
        ),
        Tool(
            name="execute_pleiades_agent",
            description="Execute a Pleiades agent to analyze and plan a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to execute"
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Detailed description of the task"
                    },
                    "repository_path": {
                        "type": "string",
                        "description": "Optional: Path to repository if task is repository-specific"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Task severity/priority"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment context"
                    }
                },
                "required": ["agent_name", "task_description"]
            }
        ),
        Tool(
            name="list_pleiades_agents",
            description="List all available Pleiades agents with their details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tier": {
                        "type": "string",
                        "enum": ["strategic", "tactical"],
                        "description": "Optional: Filter by agent tier"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter by category"
                    }
                }
            }
        ),
        Tool(
            name="get_pleiades_agent_info",
            description="Get detailed information about a specific Pleiades agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent"
                    }
                },
                "required": ["agent_name"]
            }
        ),
        Tool(
            name="get_agent_instructions",
            description="Get the full instructions (AGENT.md) for a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent"
                    }
                },
                "required": ["agent_name"]
            }
        )
    ]
    return tools


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from Claude Code."""

    if name == "list_pleiades_agents":
        tier_filter = arguments.get("tier")
        category_filter = arguments.get("category")

        agents = agent_loader.list_agents()
        result = "## Available Pleiades Agents\n\n"

        # Group by tier
        strategic = []
        tactical = []

        for agent_name in agents:
            info = agent_loader.get_agent_info(agent_name)
            if not info:
                continue

            # Apply filters
            if tier_filter and info["tier"] != tier_filter:
                continue
            if category_filter and info["category"] != category_filter:
                continue

            if info["tier"] == "strategic":
                strategic.append(info)
            else:
                tactical.append(info)

        if strategic:
            result += f"### Strategic Agents ({len(strategic)})\n\n"
            for info in strategic:
                result += f"**{info['name']}** ({info['category']})\n"
                result += f"  {info['description']}\n"
                if info['delegates_to']:
                    result += f"  Delegates to: {', '.join(info['delegates_to'])}\n"
                result += "\n"

        if tactical:
            result += f"### Tactical Agents ({len(tactical)})\n\n"
            for info in tactical:
                result += f"**{info['name']}** ({info['category']})\n"
                result += f"  {info['description']}\n"
                result += "\n"

        total = len(strategic) + len(tactical)
        result += f"\n**Total**: {total} agents"

        return [TextContent(type="text", text=result)]

    elif name == "get_pleiades_agent_info":
        agent_name = arguments["agent_name"]
        info = agent_loader.get_agent_info(agent_name)

        if not info:
            return [TextContent(type="text", text=f"Agent '{agent_name}' not found.")]

        result = f"## {info['name']}\n\n"
        result += f"**Description**: {info['description']}\n\n"
        result += f"**Tier**: {info['tier']}\n"
        result += f"**Category**: {info['category']}\n"
        result += f"**Requires Opus**: {'Yes' if info['requires_opus'] else 'No'}\n"
        result += f"**Runtime Mode**: {info['runtime_mode']}\n\n"

        if info['keywords']:
            result += "**Keywords**:\n"
            for kw in info['keywords']:
                result += f"- {kw}\n"
            result += "\n"

        if info['delegates_to']:
            result += "**Delegates To**:\n"
            for delegate in info['delegates_to']:
                result += f"- {delegate}\n"

        return [TextContent(type="text", text=result)]

    elif name == "get_agent_instructions":
        agent_name = arguments["agent_name"]
        agent = agent_loader.get_agent(agent_name)

        if not agent:
            return [TextContent(type="text", text=f"Agent '{agent_name}' not found.")]

        if not agent.instructions:
            return [TextContent(type="text", text=f"No instructions found for agent '{agent_name}'.")]

        return [TextContent(type="text", text=agent.instructions)]

    elif name == "select_pleiades_agent":
        task_description = arguments["task_description"]
        explicit_agent = arguments.get("explicit_agent")

        agent = agent_loader.select_agent(
            task_description=task_description,
            explicit_agent=explicit_agent
        )

        if not agent:
            return [TextContent(
                type="text",
                text=f"No suitable agent found for task: {task_description}"
            )]

        matched = agent.get_matched_keywords(task_description)

        result = f"## Selected Agent: {agent.name}\n\n"
        result += f"**Description**: {agent.description}\n"
        result += f"**Tier**: {agent.tier}\n"
        result += f"**Category**: {agent.category}\n\n"
        result += f"**Matched Keywords**: {', '.join(matched)}\n\n"

        if agent.delegates_to:
            result += f"**Can Delegate To**: {', '.join(agent.delegates_to)}\n\n"

        result += "Use `execute_pleiades_agent` to run this agent.\n"

        return [TextContent(type="text", text=result)]

    elif name == "execute_pleiades_agent":
        agent_name = arguments["agent_name"]
        task_description = arguments["task_description"]
        repository_path = arguments.get("repository_path")
        severity = arguments.get("severity")
        environment = arguments.get("environment")

        agent = agent_loader.get_agent(agent_name)

        if not agent:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_name}' not found."
            )]

        context = AgentContext(
            task_description=task_description,
            repository_path=repository_path,
            environment=environment,
            severity=severity
        )

        logger.info(f"Executing agent: {agent_name}")
        result = agent.run(context)

        output = f"## Agent Execution: {agent_name}\n\n"
        output += f"**Status**: {result.status}\n"
        output += f"**Message**: {result.message}\n\n"

        if result.analysis:
            output += "### Analysis\n"
            output += f"- **Tier**: {result.analysis.get('tier', 'N/A')}\n"
            output += f"- **Category**: {result.analysis.get('category', 'N/A')}\n"
            output += f"- **Matched Keywords**: {', '.join(result.analysis.get('matched_keywords', []))}\n"
            if result.analysis.get('severity'):
                output += f"- **Severity**: {result.analysis['severity']}\n"
            output += "\n"

        if result.plan:
            output += f"### Plan ({len(result.plan)} steps)\n"
            for step in result.plan:
                delegation = f" → {step['delegate_to']}" if step.get('delegate_to') else ""
                output += f"{step['step']}. {step['action']}{delegation}\n"
            output += "\n"

        if result.delegations:
            output += f"### Delegation Targets\n"
            output += f"This agent can delegate to: {', '.join(result.delegations)}\n\n"

        # Include instructions summary
        if agent.instructions:
            output += "### Agent Instructions Available\n"
            output += "Use `get_agent_instructions` to view full instructions.\n"

        return [TextContent(type="text", text=output)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the Pleiades Agents MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pleiades-agents",
                server_version="0.1.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
