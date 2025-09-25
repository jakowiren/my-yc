"""
Project Agent Orchestration for Autonomous Startup Creation
Entry point for Modal containers to execute agent swarms.
"""

import asyncio
from typing import Dict, Any
from .base_agent import AgentOrchestrator
from .github_agent import GitHubAgent


async def run_agent_swarm(project_id: str, project_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the autonomous agent swarm for startup creation.

    This is the main entry point called by modal_spawner.py.
    Creates and orchestrates specialized agents to build a complete startup.

    Args:
        project_id: Unique identifier for the project
        project_state: Current project state with configuration

    Returns:
        Dictionary with orchestration results and updated state
    """
    print(f"🚀 Starting agent swarm for project {project_id}")

    # Extract project configuration
    project_config = project_state.get("config", {})

    # Initialize agent orchestrator
    orchestrator = AgentOrchestrator(project_id, project_config)

    # MVP: Add only GitHub agent for now
    # Future agents: DatabaseAgent, DeploymentAgent, EmailAgent, etc.
    github_agent = GitHubAgent(project_id, project_config)
    orchestrator.add_agent(github_agent)

    print(f"🤖 Initialized {len(orchestrator.agents)} agents")

    # Execute all agents
    # For MVP: run sequentially (can change to parallel later)
    result = await orchestrator.run_all(parallel=False)

    # Update project state with results
    updated_state = {
        **project_state,
        "orchestration": result,
        "status": "completed" if result["success"] else "failed",
        "progress": 100 if result["success"] else project_state.get("progress", 0),
        "agents": {
            agent_result["agent_name"]: {
                "status": agent_result["final_status"],
                "progress": agent_result["final_progress"],
                "logs": len(agent_result.get("logs", [])),
                "success": agent_result.get("success", False)
            }
            for agent_result in result["results"]
            if isinstance(agent_result, dict)
        }
    }

    # Extract key service information for easy access
    if result["success"] and result["results"]:
        github_result = result["results"][0]  # First (and only) agent result
        if github_result.get("success") and "data" in github_result:
            updated_state["services"] = {
                "github": {
                    "repository_url": github_result["data"]["repository"]["url"],
                    "repository_name": github_result["data"]["repository"]["name"],
                    "clone_url": github_result["data"]["repository"]["clone_url"],
                    "deployment_url": github_result["data"]["deployment"]["vercel_url"]
                }
            }

    print(f"✅ Agent swarm completed for project {project_id}")
    print(f"📊 Success: {result['success']}, Agents: {result['successful_agents']}/{result['total_agents']}")

    return updated_state


# Future agent additions (for reference):
"""
# Example of how to add more agents later:

from .database_agent import DatabaseAgent
from .deployment_agent import DeploymentAgent
from .email_agent import EmailAgent

async def run_agent_swarm(project_id: str, project_state: Dict[str, Any]) -> Dict[str, Any]:
    orchestrator = AgentOrchestrator(project_id, project_config)

    # Add all agents
    orchestrator.add_agent(GitHubAgent(project_id, project_config))
    orchestrator.add_agent(DatabaseAgent(project_id, project_config))  # Supabase setup
    orchestrator.add_agent(DeploymentAgent(project_id, project_config))  # Vercel deploy
    orchestrator.add_agent(EmailAgent(project_id, project_config))  # Email setup

    # Run in parallel for faster execution
    result = await orchestrator.run_all(parallel=True)
    return updated_state
"""