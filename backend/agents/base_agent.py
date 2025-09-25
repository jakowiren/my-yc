"""
Base Agent Framework for Modal-based Autonomous Startup Creation
Provides foundation for specialized agents with embedded MCP tools.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all autonomous startup agents."""

    def __init__(self, project_id: str, project_config: Dict[str, Any]):
        """
        Initialize base agent.

        Args:
            project_id: Unique identifier for the project
            project_config: Project configuration including idea, target market, etc.
        """
        self.project_id = project_id
        self.project_config = project_config
        self.agent_name = self.__class__.__name__.lower().replace("agent", "")
        self.status = "initialized"
        self.progress = 0
        self.logs: List[Dict[str, Any]] = []

    async def log(self, message: str, level: str = "info", data: Optional[Dict[str, Any]] = None):
        """Log agent activity."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "level": level,
            "message": message,
            "data": data or {}
        }
        self.logs.append(log_entry)
        print(f"🤖 [{self.agent_name}] {level.upper()}: {message}")

    async def update_status(self, status: str, progress: Optional[int] = None):
        """Update agent status and progress."""
        self.status = status
        if progress is not None:
            self.progress = progress
        await self.log(f"Status: {status}" + (f" ({progress}%)" if progress is not None else ""))

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        Must be implemented by each agent.

        Returns:
            Dictionary with execution results
        """
        pass

    async def run(self) -> Dict[str, Any]:
        """
        Run the agent with proper error handling and logging.

        Returns:
            Dictionary with execution results and metadata
        """
        await self.log(f"Starting {self.agent_name} agent execution")
        await self.update_status("running", 0)

        try:
            result = await self.execute()

            if result.get("success", False):
                await self.update_status("completed", 100)
                await self.log("Agent execution completed successfully")
            else:
                await self.update_status("failed")
                await self.log(f"Agent execution failed: {result.get('error', 'Unknown error')}", "error")

            return {
                **result,
                "agent_name": self.agent_name,
                "project_id": self.project_id,
                "final_status": self.status,
                "final_progress": self.progress,
                "logs": self.logs
            }

        except Exception as e:
            await self.update_status("error")
            await self.log(f"Unexpected error during execution: {str(e)}", "error")

            return {
                "success": False,
                "error": str(e),
                "agent_name": self.agent_name,
                "project_id": self.project_id,
                "final_status": self.status,
                "final_progress": self.progress,
                "logs": self.logs
            }


class AgentOrchestrator:
    """Orchestrates multiple agents for startup creation."""

    def __init__(self, project_id: str, project_config: Dict[str, Any]):
        """
        Initialize agent orchestrator.

        Args:
            project_id: Unique identifier for the project
            project_config: Project configuration
        """
        self.project_id = project_id
        self.project_config = project_config
        self.agents: List[BaseAgent] = []
        self.results: List[Dict[str, Any]] = []

    def add_agent(self, agent: BaseAgent):
        """Add an agent to the orchestration."""
        self.agents.append(agent)

    async def run_all(self, parallel: bool = False) -> Dict[str, Any]:
        """
        Run all registered agents.

        Args:
            parallel: Whether to run agents in parallel or sequentially

        Returns:
            Dictionary with orchestration results
        """
        print(f"🚀 Starting orchestration for project {self.project_id}")
        print(f"📊 Running {len(self.agents)} agents {'in parallel' if parallel else 'sequentially'}")

        if parallel:
            # Run all agents in parallel
            tasks = [agent.run() for agent in self.agents]
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run agents sequentially
            for agent in self.agents:
                result = await agent.run()
                self.results.append(result)

                # Stop if an agent fails (optional: could continue with warnings)
                if not result.get("success", False):
                    print(f"⚠️ Agent {agent.agent_name} failed, stopping orchestration")
                    break

        # Summarize results
        successful_agents = sum(1 for result in self.results if isinstance(result, dict) and result.get("success", False))
        failed_agents = len(self.results) - successful_agents

        return {
            "success": failed_agents == 0,
            "project_id": self.project_id,
            "total_agents": len(self.agents),
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "results": self.results,
            "summary": f"Completed {successful_agents}/{len(self.agents)} agents successfully"
        }