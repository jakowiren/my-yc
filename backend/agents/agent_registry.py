"""
Agent Registry Service - Service discovery for autonomous agents
Provides additive-only functionality without modifying existing agents
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum


class AgentType(Enum):
    """Types of agents in the my-yc ecosystem"""
    CEO = "ceo"
    FRONTEND_DEVELOPER = "frontend_developer"
    BACKEND_DEVELOPER = "backend_developer"
    DEVOPS = "devops"
    QA = "qa"
    DESIGNER = "designer"


class AgentStatus(Enum):
    """Agent operational status"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    INITIALIZING = "initializing"


class AgentCapability:
    """Represents a capability that an agent can perform"""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}


class RegisteredAgent:
    """Information about a registered agent"""

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        startup_id: str,
        endpoint: str,
        capabilities: List[AgentCapability] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.startup_id = startup_id
        self.endpoint = endpoint
        self.capabilities = capabilities or []
        self.status = AgentStatus.INITIALIZING
        self.last_heartbeat = datetime.now()
        self.registration_time = datetime.now()
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "startup_id": self.startup_id,
            "endpoint": self.endpoint,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "registration_time": self.registration_time.isoformat(),
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "parameters": cap.parameters
                }
                for cap in self.capabilities
            ],
            "metadata": self.metadata
        }


class AgentRegistry:
    """
    Service discovery and management for autonomous agents.

    This is an additive service that tracks agents without modifying them.
    Existing agents (like CEO) can optionally register themselves.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the agent registry"""
        self.registry_path = registry_path or Path("/tmp/agent_registry")
        self.registry_path.mkdir(parents=True, exist_ok=True)

        # In-memory registry for fast access
        self.agents: Dict[str, RegisteredAgent] = {}

        # Load existing registry if available
        self._load_registry()

    def register_agent(
        self,
        agent_type: AgentType,
        startup_id: str,
        endpoint: str,
        agent_id: Optional[str] = None,
        capabilities: List[AgentCapability] = None
    ) -> str:
        """
        Register a new agent.

        Args:
            agent_type: Type of agent being registered
            startup_id: ID of the startup this agent belongs to
            endpoint: HTTP endpoint where agent can be reached
            agent_id: Optional custom agent ID (auto-generated if not provided)
            capabilities: List of capabilities this agent provides

        Returns:
            Agent ID for the registered agent
        """
        if agent_id is None:
            agent_id = f"{agent_type.value}_{startup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        agent = RegisteredAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            startup_id=startup_id,
            endpoint=endpoint,
            capabilities=capabilities or []
        )

        self.agents[agent_id] = agent
        self._save_registry()

        print(f"📋 Registered {agent_type.value} agent: {agent_id} for startup: {startup_id}")
        return agent_id

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.

        Args:
            agent_id: ID of agent to unregister

        Returns:
            True if agent was found and removed, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save_registry()
            print(f"📋 Unregistered agent: {agent_id}")
            return True
        return False

    def update_agent_status(self, agent_id: str, status: AgentStatus, metadata: Dict[str, Any] = None) -> bool:
        """
        Update an agent's status and metadata.

        Args:
            agent_id: ID of agent to update
            status: New status
            metadata: Additional metadata to store

        Returns:
            True if agent was found and updated, False otherwise
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = status
            agent.last_heartbeat = datetime.now()
            if metadata:
                agent.metadata.update(metadata)
            self._save_registry()
            return True
        return False

    def heartbeat(self, agent_id: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Record a heartbeat from an agent.

        Args:
            agent_id: ID of agent sending heartbeat
            metadata: Optional metadata update

        Returns:
            True if agent was found, False otherwise
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.last_heartbeat = datetime.now()
            if agent.status == AgentStatus.INITIALIZING:
                agent.status = AgentStatus.ONLINE
            if metadata:
                agent.metadata.update(metadata)
            self._save_registry()
            return True
        return False

    def get_agents_for_startup(self, startup_id: str) -> List[RegisteredAgent]:
        """
        Get all agents registered for a specific startup.

        Args:
            startup_id: ID of startup

        Returns:
            List of registered agents for the startup
        """
        return [
            agent for agent in self.agents.values()
            if agent.startup_id == startup_id
        ]

    def get_agents_by_type(self, agent_type: AgentType, startup_id: Optional[str] = None) -> List[RegisteredAgent]:
        """
        Get all agents of a specific type.

        Args:
            agent_type: Type of agents to find
            startup_id: Optional filter by startup ID

        Returns:
            List of agents matching the criteria
        """
        agents = [
            agent for agent in self.agents.values()
            if agent.agent_type == agent_type
        ]

        if startup_id:
            agents = [agent for agent in agents if agent.startup_id == startup_id]

        return agents

    def get_online_agents(self, startup_id: Optional[str] = None) -> List[RegisteredAgent]:
        """
        Get all currently online agents.

        Args:
            startup_id: Optional filter by startup ID

        Returns:
            List of online agents
        """
        cutoff_time = datetime.now() - timedelta(minutes=5)  # 5 minute timeout

        online_agents = []
        for agent in self.agents.values():
            if agent.last_heartbeat > cutoff_time and agent.status != AgentStatus.OFFLINE:
                if startup_id is None or agent.startup_id == startup_id:
                    online_agents.append(agent)

        return online_agents

    async def health_check(self, agent_endpoint: str, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Perform health check on an agent endpoint.

        Args:
            agent_endpoint: HTTP endpoint to check
            timeout: Timeout in seconds

        Returns:
            Health check result
        """
        try:
            import httpx

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{agent_endpoint}/health")

                if response.status_code == 200:
                    return {
                        "healthy": True,
                        "status_code": response.status_code,
                        "response": response.json(),
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": response.status_code,
                        "error": "Non-200 status code"
                    }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def health_check_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health checks on all registered agents.

        Returns:
            Dictionary mapping agent_id to health check results
        """
        health_results = {}

        tasks = []
        for agent_id, agent in self.agents.items():
            tasks.append(self._health_check_agent(agent_id, agent))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                agent_id = list(self.agents.keys())[i]
                if isinstance(result, Exception):
                    health_results[agent_id] = {
                        "healthy": False,
                        "error": str(result)
                    }
                else:
                    health_results[agent_id] = result

        return health_results

    async def _health_check_agent(self, agent_id: str, agent: RegisteredAgent) -> Dict[str, Any]:
        """Internal helper for health checking a single agent"""
        health_result = await self.health_check(agent.endpoint)

        # Update agent status based on health check
        if health_result["healthy"]:
            self.update_agent_status(agent_id, AgentStatus.ONLINE)
        else:
            self.update_agent_status(agent_id, AgentStatus.ERROR, {
                "last_error": health_result.get("error", "Health check failed"),
                "last_error_time": datetime.now().isoformat()
            })

        return health_result

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get overall registry status and statistics.

        Returns:
            Registry status information
        """
        startup_count = len(set(agent.startup_id for agent in self.agents.values()))
        agents_by_type = {}
        agents_by_status = {}

        for agent in self.agents.values():
            # Count by type
            agent_type = agent.agent_type.value
            agents_by_type[agent_type] = agents_by_type.get(agent_type, 0) + 1

            # Count by status
            status = agent.status.value
            agents_by_status[status] = agents_by_status.get(status, 0) + 1

        return {
            "total_agents": len(self.agents),
            "total_startups": startup_count,
            "agents_by_type": agents_by_type,
            "agents_by_status": agents_by_status,
            "registry_path": str(self.registry_path),
            "last_updated": datetime.now().isoformat()
        }

    def _load_registry(self):
        """Load registry from persistent storage"""
        registry_file = self.registry_path / "agents.json"

        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)

                for agent_data in data.get("agents", []):
                    agent = RegisteredAgent(
                        agent_id=agent_data["agent_id"],
                        agent_type=AgentType(agent_data["agent_type"]),
                        startup_id=agent_data["startup_id"],
                        endpoint=agent_data["endpoint"]
                    )

                    # Restore status and timestamps
                    agent.status = AgentStatus(agent_data["status"])
                    agent.last_heartbeat = datetime.fromisoformat(agent_data["last_heartbeat"])
                    agent.registration_time = datetime.fromisoformat(agent_data["registration_time"])
                    agent.metadata = agent_data.get("metadata", {})

                    # Restore capabilities
                    for cap_data in agent_data.get("capabilities", []):
                        capability = AgentCapability(
                            name=cap_data["name"],
                            description=cap_data["description"],
                            parameters=cap_data["parameters"]
                        )
                        agent.capabilities.append(capability)

                    self.agents[agent.agent_id] = agent

                print(f"📋 Loaded {len(self.agents)} agents from registry")

            except Exception as e:
                print(f"⚠️ Failed to load agent registry: {e}")

    def _save_registry(self):
        """Save registry to persistent storage"""
        registry_file = self.registry_path / "agents.json"

        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "agents": [agent.to_dict() for agent in self.agents.values()]
            }

            with open(registry_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to save agent registry: {e}")


# Global registry instance for easy access
_global_registry: Optional[AgentRegistry] = None


def get_global_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


# Convenience functions for common operations
def register_ceo_agent(startup_id: str, endpoint: str) -> str:
    """Quick registration for CEO agents"""
    registry = get_global_registry()

    # CEO capabilities
    capabilities = [
        AgentCapability("project_initialization", "Initialize and create GitHub repositories"),
        AgentCapability("team_planning", "Plan development teams and architecture"),
        AgentCapability("code_review", "Review and provide feedback on code"),
        AgentCapability("strategic_decisions", "Make high-level strategic decisions"),
        AgentCapability("stakeholder_communication", "Communicate with founders and investors")
    ]

    return registry.register_agent(
        agent_type=AgentType.CEO,
        startup_id=startup_id,
        endpoint=endpoint,
        capabilities=capabilities
    )


def get_startup_team_status(startup_id: str) -> Dict[str, Any]:
    """Get comprehensive team status for a startup"""
    registry = get_global_registry()
    agents = registry.get_agents_for_startup(startup_id)

    team_status = {
        "startup_id": startup_id,
        "total_agents": len(agents),
        "agents": {},
        "capabilities": []
    }

    for agent in agents:
        team_status["agents"][agent.agent_type.value] = {
            "agent_id": agent.agent_id,
            "status": agent.status.value,
            "endpoint": agent.endpoint,
            "last_heartbeat": agent.last_heartbeat.isoformat(),
            "capabilities_count": len(agent.capabilities)
        }

        # Collect all capabilities
        for capability in agent.capabilities:
            team_status["capabilities"].append({
                "agent_type": agent.agent_type.value,
                "capability": capability.name,
                "description": capability.description
            })

    return team_status


if __name__ == "__main__":
    # Test the registry
    registry = AgentRegistry()

    # Register a test CEO
    ceo_id = register_ceo_agent("test-startup-123", "https://test-ceo-endpoint.com")
    print(f"Registered CEO: {ceo_id}")

    # Get status
    status = registry.get_registry_status()
    print(f"Registry status: {status}")

    # Get team status
    team_status = get_startup_team_status("test-startup-123")
    print(f"Team status: {team_status}")