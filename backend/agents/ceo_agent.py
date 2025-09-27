"""
CEO Agent - Refactored with Clean MCP Architecture
Autonomous leader focused on strategy, not tool plumbing.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI
from github import Github


class CEOAgent:
    """
    Clean CEO Agent that focuses on strategic thinking.
    All tool complexity is handled by the MCP framework.
    """

    def __init__(self, startup_id: str, design_doc: Dict[str, Any], workspace_manager=None, github_token: str = None):
        self.startup_id = startup_id
        self.startup_name = design_doc.get("title", f"Startup {startup_id}")
        self.design_doc = design_doc

        # Initialize OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai = OpenAI(api_key=openai_key)

        # Set up workspace paths
        self.workspace_manager = workspace_manager
        if workspace_manager:
            self.workspace_path = workspace_manager.get_workspace_path(startup_id)
            self.memory_path = self.workspace_path / "memory"
        else:
            self.workspace_path = None
            self.memory_path = None

        # Initialize MCP tools with clean auto-registration
        self.mcp_tools = None
        if self.workspace_path:
            try:
                # Import with fallbacks for different environments
                import sys
                sys.path.insert(0, "/root")
                from mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP
            except ImportError:
                from .mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP

            # Clean tool registration - MCP framework handles everything else
            self.mcp_tools = MCPToolRegistry(self.workspace_path, startup_id)
            self.mcp_tools.register_tool("filesystem", FileSystemMCP)
            self.mcp_tools.register_tool("git", GitMCP)
            self.mcp_tools.register_tool("documentation", DocumentationMCP)
            self.mcp_tools.register_tool("github", GitHubCoordinationMCP, github_token=github_token)

        # State (loaded from workspace if available)
        self.conversation_history: List[Dict[str, str]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.status = "initialized"
        self.repo_url = design_doc.get("github_repo_url")

        # Load existing state if workspace exists
        if self.memory_path and self.memory_path.exists():
            self.load_state()

    async def handle_work_request_streaming(self, request: str):
        """
        Handle work requests with streaming response.
        Clean and simple - MCP framework handles all complexity.
        """
        if not self.mcp_tools:
            yield {"type": "content", "content": "I need a workspace to handle work requests. Please initialize the CEO first."}
            return

        # Add to conversation history
        self.add_conversation("user", request)

        try:
            # Get auto-discovered tools from MCP framework
            tools = self.mcp_tools.get_all_openai_functions()

            # Build conversation with memory
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
                save_conversation_callback=lambda content: self.add_conversation("ceo", content)
            ):
                if chunk.get("type") == "content":
                    full_response += chunk.get("content", "")
                yield chunk

            # Save state
            self.save_state()

        except Exception as e:
            error_msg = f"I encountered an issue: {str(e)}"
            self.add_conversation("ceo", error_msg)
            self.save_state()
            yield {"type": "content", "content": error_msg}

    def _build_conversation_context(self, request: str) -> List[Dict[str, str]]:
        """Build conversation context with system prompt and history."""
        messages = [
            {
                "role": "system",
                "content": f"""You are the CEO of {self.startup_name}, an AI-managed startup.

Your role:
- Strategic oversight and coordination
- Understanding project status and progress
- Making high-level decisions about features and direction
- Managing all aspects of the project including files, documentation, and GitHub

Your capabilities:
- You CAN read, write, and modify any project files
- You CAN create documentation, specifications, and TODO items
- You CAN manage GitHub issues and milestones
- You CAN analyze code structure and git history
- You ARE the decision-maker and executor, not just an advisor

Your personality:
- Professional but approachable
- Strategic thinker
- Action-oriented - you get things done
- Transparent about what you're doing when you use tools
- Focused on business value and user needs

Use the available tools to both gather information AND take action as needed.

IMPORTANT MEMORY CONTEXT:
- You have full memory of all previous conversations and decisions
- You maintain persistent state in your workspace at {self.workspace_path}
- Reference past interactions, decisions, and project history when relevant
- Use your tools to access project files and documentation for additional context
- You are the same CEO instance across all conversations - maintain continuity

Current startup context:
- Startup: {self.startup_name}
- Repository: {'Available' if self.repo_url else 'Not set up yet'}"""
            }
        ]

        # Add conversation history for context
        recent_history = self.conversation_history[-20:]  # Last 20 messages
        for entry in recent_history:
            if entry.get("role") in ["user", "ceo"]:
                role = "assistant" if entry["role"] == "ceo" else entry["role"]
                messages.append({
                    "role": role,
                    "content": entry["message"]
                })

        # Add current request
        messages.append({
            "role": "user",
            "content": request
        })

        return messages

    def add_conversation(self, role: str, message: str):
        """Add conversation entry with timestamp."""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def save_state(self):
        """Save CEO state to persistent workspace."""
        if not self.memory_path:
            return

        try:
            self.memory_path.mkdir(parents=True, exist_ok=True)

            state = {
                "startup_id": self.startup_id,
                "startup_name": self.startup_name,
                "status": self.status,
                "last_active": datetime.now().isoformat(),
                "conversation_history": self.conversation_history,
                "decisions": self.decisions,
                "repo_url": self.repo_url,
            }

            with open(self.memory_path / "state.json", "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"❌ Failed to save CEO state: {e}")

    def load_state(self):
        """Load CEO state from persistent workspace."""
        if not self.memory_path or not (self.memory_path / "state.json").exists():
            return

        try:
            with open(self.memory_path / "state.json", "r") as f:
                state = json.load(f)

            # Restore state
            self.status = state.get("status", "initialized")
            self.conversation_history = state.get("conversation_history", [])
            self.decisions = state.get("decisions", [])
            self.repo_url = state.get("repo_url")

            print(f"📁 CEO state loaded: {len(self.conversation_history)} conversations, {len(self.decisions)} decisions")

        except Exception as e:
            print(f"❌ Failed to load CEO state: {e}")