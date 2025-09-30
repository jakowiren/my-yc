"""
PersistentAgent Base Class - Foundation for all autonomous agents
Provides standardized workspace management, MCP tool integration, and state persistence
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator
from openai import OpenAI


class PersistentAgent(ABC):
    """
    Base class for all persistent autonomous agents in my-yc.

    This class provides:
    - Standardized workspace management
    - MCP tool integration
    - State persistence across container restarts
    - Conversation memory management
    - Inter-agent communication foundation

    Future agents (Frontend Developer, Backend Developer, etc.) inherit from this.
    """

    def __init__(
        self,
        startup_id: str,
        agent_type: str,
        workspace_manager=None,
        design_doc: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a persistent agent.

        Args:
            startup_id: Unique identifier for the startup
            agent_type: Type of agent (e.g., "frontend_developer", "backend_developer")
            workspace_manager: Workspace manager instance
            design_doc: Optional design document for context
        """
        self.startup_id = startup_id
        self.agent_type = agent_type
        self.design_doc = design_doc or {}

        # Initialize OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai = OpenAI(api_key=openai_key)

        # Set up workspace paths
        self.workspace_manager = workspace_manager
        if workspace_manager:
            self.workspace_path = workspace_manager.get_workspace_path(startup_id)
            self.memory_path = self.workspace_path / "memory" / agent_type
            self.shared_memory_path = self.workspace_path / "memory" / "shared"
        else:
            self.workspace_path = None
            self.memory_path = None
            self.shared_memory_path = None

        # Initialize MCP tools with clean auto-registration
        self.mcp_tools = None
        if self.workspace_path:
            self._setup_mcp_tools()

        # Agent state (loaded from workspace if available)
        self.conversation_history: List[Dict[str, str]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.status = "initialized"
        self.specialization = self._get_agent_specialization()
        self.capabilities = self._get_agent_capabilities()

        # Ensure memory directories exist
        if self.memory_path:
            self.memory_path.mkdir(parents=True, exist_ok=True)

        # Load existing state if workspace exists
        if self.memory_path and self.memory_path.exists():
            self.load_state()

    def _setup_mcp_tools(self):
        """Setup MCP tools for this agent. Uses same pattern as CEO."""
        try:
            # Import with fallbacks for different environments
            import sys
            if "/root" not in sys.path:
                sys.path.insert(0, "/root")

            from mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP

            # Clean tool registration - MCP framework handles everything else
            self.mcp_tools = MCPToolRegistry(self.workspace_path, self.startup_id)
            self.mcp_tools.register_tool("filesystem", FileSystemMCP)
            self.mcp_tools.register_tool("git", GitMCP)
            self.mcp_tools.register_tool("documentation", DocumentationMCP)

            # Let subclasses add specialized tools
            self._register_specialized_tools()

        except ImportError as e:
            print(f"⚠️ MCP tools not available: {e}")

    def _register_specialized_tools(self):
        """
        Override in subclasses to register agent-specific MCP tools.

        Example for Frontend Developer:
            self.mcp_tools.register_tool("react", ReactMCP)
            self.mcp_tools.register_tool("styling", StylingMCP)
        """
        pass

    @abstractmethod
    def _get_agent_specialization(self) -> Dict[str, Any]:
        """
        Return agent's specialization details.

        Returns:
            Dictionary describing the agent's role, focus areas, and expertise
        """
        pass

    @abstractmethod
    def _get_agent_capabilities(self) -> List[str]:
        """
        Return list of capabilities this agent provides.

        Returns:
            List of capability names
        """
        pass

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent type.

        Returns:
            System prompt string that defines the agent's role and behavior
        """
        pass

    async def handle_work_request_streaming(self, request: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Handle work requests with streaming response.
        Uses same pattern as CEO but allows for agent-specific behavior.

        Args:
            request: Work request from user or other agents

        Yields:
            Streaming response chunks
        """
        if not self.mcp_tools:
            yield {"type": "content", "content": f"I need a workspace to handle requests. Please initialize the {self.agent_type} first."}
            return

        # Add to conversation history
        self.add_conversation("user", request)

        try:
            # Get auto-discovered tools from MCP framework
            tools = self.mcp_tools.get_all_openai_functions()

            # Build conversation with memory and agent-specific context
            messages = self._build_conversation_context(request)

            # Stream OpenAI response
            response_stream = self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                stream=True
            )

            # Let MCP framework handle everything (streaming + tool execution)
            full_response = ""
            async for chunk in self.mcp_tools.handle_streaming_response(
                response_stream,
                save_conversation_callback=lambda content: self.add_conversation(self.agent_type, content)
            ):
                if chunk.get("type") == "content":
                    full_response += chunk.get("content", "")
                yield chunk

            # Save state after each interaction
            self.save_state()

        except Exception as e:
            error_msg = f"I encountered an issue: {str(e)}"
            self.add_conversation(self.agent_type, error_msg)
            self.save_state()
            yield {"type": "content", "content": error_msg}

    def _build_conversation_context(self, request: str) -> List[Dict[str, str]]:
        """Build conversation context with system prompt and history."""
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]

        # Add recent conversation history (last 10 exchanges)
        recent_history = self.conversation_history[-20:] if len(self.conversation_history) > 20 else self.conversation_history

        for entry in recent_history:
            messages.append({
                "role": "user" if entry["role"] == "user" else "assistant",
                "content": entry["content"]
            })

        # Add current request
        messages.append({
            "role": "user",
            "content": request
        })

        return messages

    def add_conversation(self, role: str, content: str):
        """Add entry to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(entry)

    def add_decision(self, decision_type: str, context: str, decision: str, reasoning: str):
        """Record a decision made by this agent."""
        decision_entry = {
            "type": decision_type,
            "context": context,
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "agent_type": self.agent_type
        }
        self.decisions.append(decision_entry)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of this agent."""
        return {
            "agent_type": self.agent_type,
            "startup_id": self.startup_id,
            "status": self.status,
            "specialization": self.specialization,
            "capabilities": self.capabilities,
            "conversation_count": len(self.conversation_history),
            "decisions_count": len(self.decisions),
            "workspace_path": str(self.workspace_path) if self.workspace_path else None,
            "mcp_tools_available": self.mcp_tools is not None,
            "last_activity": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }

    def save_state(self):
        """Save agent state to workspace."""
        if not self.memory_path:
            return

        try:
            # Save conversation history
            conversation_file = self.memory_path / "conversations.jsonl"
            with open(conversation_file, "w") as f:
                for entry in self.conversation_history:
                    f.write(json.dumps(entry) + "\n")

            # Save decisions
            decisions_file = self.memory_path / "decisions.jsonl"
            with open(decisions_file, "w") as f:
                for decision in self.decisions:
                    f.write(json.dumps(decision) + "\n")

            # Save agent metadata
            metadata_file = self.memory_path / "metadata.json"
            metadata = {
                "agent_type": self.agent_type,
                "startup_id": self.startup_id,
                "status": self.status,
                "specialization": self.specialization,
                "capabilities": self.capabilities,
                "last_saved": datetime.now().isoformat()
            }
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Call agent-specific state saving
            self._save_agent_specific_state()

        except Exception as e:
            print(f"⚠️ Failed to save {self.agent_type} state: {e}")

    def load_state(self):
        """Load agent state from workspace."""
        if not self.memory_path:
            return

        try:
            # Load conversation history
            conversation_file = self.memory_path / "conversations.jsonl"
            if conversation_file.exists():
                self.conversation_history = []
                with open(conversation_file, "r") as f:
                    for line in f:
                        if line.strip():
                            self.conversation_history.append(json.loads(line.strip()))

            # Load decisions
            decisions_file = self.memory_path / "decisions.jsonl"
            if decisions_file.exists():
                self.decisions = []
                with open(decisions_file, "r") as f:
                    for line in f:
                        if line.strip():
                            self.decisions.append(json.loads(line.strip()))

            # Load metadata
            metadata_file = self.memory_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    self.status = metadata.get("status", "initialized")

            # Call agent-specific state loading
            self._load_agent_specific_state()

            print(f"📁 Loaded {self.agent_type} state: {len(self.conversation_history)} conversations, {len(self.decisions)} decisions")

        except Exception as e:
            print(f"⚠️ Failed to load {self.agent_type} state: {e}")

    def _save_agent_specific_state(self):
        """Override in subclasses to save agent-specific state."""
        pass

    def _load_agent_specific_state(self):
        """Override in subclasses to load agent-specific state."""
        pass

    async def communicate_with_agent(self, target_agent_type: str, message: str) -> Dict[str, Any]:
        """
        Send message to another agent in the same startup.

        Args:
            target_agent_type: Type of agent to communicate with
            message: Message to send

        Returns:
            Response from the target agent or error information
        """
        if not self.shared_memory_path:
            return {"error": "No shared workspace available for communication"}

        # Simple file-based communication for now
        # Future: Replace with proper message bus
        try:
            message_data = {
                "from": self.agent_type,
                "to": target_agent_type,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "startup_id": self.startup_id
            }

            # Write message to shared communication file
            comm_file = self.shared_memory_path / f"comm_{target_agent_type}.jsonl"
            with open(comm_file, "a") as f:
                f.write(json.dumps(message_data) + "\n")

            return {"success": True, "message_sent": True}

        except Exception as e:
            return {"error": f"Failed to send message: {e}"}

    def get_messages_from_agents(self) -> List[Dict[str, Any]]:
        """
        Get messages sent to this agent from other agents.

        Returns:
            List of messages received
        """
        if not self.shared_memory_path:
            return []

        try:
            comm_file = self.shared_memory_path / f"comm_{self.agent_type}.jsonl"
            if not comm_file.exists():
                return []

            messages = []
            with open(comm_file, "r") as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line.strip()))

            return messages

        except Exception as e:
            print(f"⚠️ Failed to load messages: {e}")
            return []

    async def initialize_agent(self) -> Dict[str, Any]:
        """
        Initialize the agent. Override in subclasses for specialized initialization.

        Returns:
            Initialization result
        """
        self.status = "ready"
        self.save_state()

        return {
            "success": True,
            "agent_type": self.agent_type,
            "startup_id": self.startup_id,
            "status": self.status,
            "message": f"{self.agent_type} agent initialized and ready"
        }


# Test agent implementation for validation
class TestEmployee(PersistentAgent):
    """Test implementation of PersistentAgent for validation."""

    def _get_agent_specialization(self) -> Dict[str, Any]:
        return {
            "role": "Test Employee",
            "focus_areas": ["Testing", "Validation", "Quality Assurance"],
            "expertise_level": "Senior",
            "primary_responsibilities": [
                "Validate base agent functionality",
                "Test MCP tool integration",
                "Ensure state persistence works"
            ]
        }

    def _get_agent_capabilities(self) -> List[str]:
        return [
            "run_tests",
            "validate_functionality",
            "check_state_persistence",
            "verify_mcp_tools"
        ]

    def _get_system_prompt(self) -> str:
        return f"""You are a Test Employee for {self.startup_id}, focused on validating system functionality.

Your role:
- Test and validate base agent capabilities
- Verify MCP tool integration works correctly
- Ensure state persistence across sessions
- Report any issues or anomalies

Your capabilities:
- You CAN read, write, and modify files in the workspace
- You CAN run tests and validation checks
- You CAN create documentation about test results
- You ARE responsible for quality assurance

Your personality:
- Methodical and thorough
- Detail-oriented
- Clear communicator about issues
- Focused on reliability and correctness

Use the available tools to test functionality and provide detailed reports.

IMPORTANT MEMORY CONTEXT:
- You have full memory of all previous interactions
- You maintain persistent state in your workspace at {self.workspace_path}
- Reference past test results and validation history when relevant
- You are the same Test Employee instance across all conversations
"""


if __name__ == "__main__":
    # Test the base class with TestEmployee
    print("🧪 Testing PersistentAgent base class...")

    try:
        # This would normally be called with proper workspace manager
        test_agent = TestEmployee(
            startup_id="test-startup-123",
            agent_type="test_employee"
        )

        print(f"✅ Created test agent: {test_agent.agent_type}")
        print(f"📊 Agent status: {test_agent.get_agent_status()}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    print("🎉 PersistentAgent base class ready for use!")