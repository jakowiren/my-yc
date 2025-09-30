"""
Agent Orchestrator - Routes requests to different LLM agents within a startup workspace
Each agent is an OpenAI conversation with persistent memory, not a running process.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from openai import OpenAI
from pathlib import Path


class AgentOrchestrator:
    """
    Orchestrates multiple LLM agents within a startup workspace.
    Each agent maintains separate conversation history and system prompt.
    """

    def __init__(self, startup_id: str, workspace_manager):
        self.startup_id = startup_id
        self.workspace_manager = workspace_manager
        self.workspace_path = workspace_manager.get_workspace_path(startup_id)
        self.agents_memory_path = self.workspace_path / "memory" / "agents"

        # Initialize OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai = OpenAI(api_key=openai_key)

        # Initialize MCP tools with clean auto-registration
        self.mcp_tools = None
        try:
            # Import with fallbacks for different environments
            import sys
            sys.path.insert(0, "/root")
            from mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP, TeamToolsMCP
        except ImportError:
            from .mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP, TeamToolsMCP

        # Set up MCP tools for the workspace
        if self.workspace_path:
            github_token = os.getenv("GITHUB_TOKEN")
            self.mcp_tools = MCPToolRegistry(self.workspace_path, startup_id)
            self.mcp_tools.register_tool("filesystem", FileSystemMCP)
            self.mcp_tools.register_tool("git", GitMCP)
            self.mcp_tools.register_tool("documentation", DocumentationMCP)
            self.mcp_tools.register_tool("github", GitHubCoordinationMCP, github_token=github_token)
            self.mcp_tools.register_tool("team", TeamToolsMCP)  # For team message board

    async def initialize_agent(self, agent_type: str, design_doc: Dict[str, Any] = None):
        """Initialize an agent with empty conversation history."""
        agent_path = self.agents_memory_path / agent_type
        agent_path.mkdir(parents=True, exist_ok=True)

        # Initialize conversation history if it doesn't exist
        conversation_file = agent_path / "conversation.json"
        if not conversation_file.exists():
            initial_conversation = {
                "agent_type": agent_type,
                "startup_id": self.startup_id,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "conversation_count": 0,
                "messages": []
            }

            with open(conversation_file, "w") as f:
                json.dump(initial_conversation, f, indent=2)

        # Initialize agent state
        state_file = agent_path / "state.json"
        if not state_file.exists():
            initial_state = {
                "agent_type": agent_type,
                "status": "initialized",
                "current_task": None,
                "last_tool_used": None,
                "design_context": design_doc,
                "created_at": datetime.now().isoformat()
            }

            with open(state_file, "w") as f:
                json.dump(initial_state, f, indent=2)

        print(f"✅ Agent '{agent_type}' initialized for startup {self.startup_id}")

    def load_agent_memory(self, agent_type: str) -> List[Dict[str, str]]:
        """Load conversation history for a specific agent."""
        conversation_file = self.agents_memory_path / agent_type / "conversation.json"

        if not conversation_file.exists():
            print(f"📝 No existing conversation for agent '{agent_type}', starting fresh")
            return []

        try:
            with open(conversation_file, "r") as f:
                data = json.load(f)
                messages = data.get("messages", [])
                print(f"📚 Loaded {len(messages)} messages for agent '{agent_type}'")
                return messages
        except Exception as e:
            print(f"❌ Error loading memory for agent '{agent_type}': {e}")
            return []

    def save_agent_memory(self, agent_type: str, new_message: Dict[str, str]):
        """Save new message to agent's conversation history."""
        agent_path = self.agents_memory_path / agent_type
        agent_path.mkdir(parents=True, exist_ok=True)

        conversation_file = agent_path / "conversation.json"

        # Load existing conversation
        if conversation_file.exists():
            with open(conversation_file, "r") as f:
                data = json.load(f)
        else:
            data = {
                "agent_type": agent_type,
                "startup_id": self.startup_id,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }

        # Add new message
        data["messages"].append(new_message)
        data["last_active"] = datetime.now().isoformat()
        data["conversation_count"] = len(data["messages"])

        # Save back to file
        with open(conversation_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Saved message for agent '{agent_type}' (total: {len(data['messages'])})")

    def get_agent_system_prompt(self, agent_type: str) -> str:
        """Get system prompt for a specific agent type."""
        try:
            from agent_configs import AGENT_CONFIGS
            config = AGENT_CONFIGS.get(agent_type)
            if not config:
                raise ValueError(f"Unknown agent type: {agent_type}")

            # Customize prompt with startup context
            workspace_info = self.workspace_manager.get_workspace_info(self.startup_id)
            startup_name = workspace_info.get("metadata", {}).get("startup_name", f"Startup {self.startup_id}")

            system_prompt = config["system_prompt"].format(
                startup_name=startup_name,
                startup_id=self.startup_id,
                workspace_path=self.workspace_path
            )

            return system_prompt

        except ImportError:
            # Fallback system prompt
            return f"""You are a {agent_type.title()} Agent for startup {self.startup_id}.

Your role and responsibilities depend on your agent type.
You have access to tools for file operations, git operations, and team communication.
You maintain persistent memory across conversations.
Always be helpful, professional, and focused on the startup's success.

Current workspace: {self.workspace_path}
"""

    def get_agent_tools(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get tools available to a specific agent type."""
        if not self.mcp_tools:
            print(f"❌ No MCP tools available for agent '{agent_type}'")
            return []

        try:
            from agent_configs import AGENT_CONFIGS
            config = AGENT_CONFIGS.get(agent_type, {})
            allowed_tools = config.get("allowed_tools", ["filesystem", "team"])

            # Get all tools and filter by allowed ones
            all_tools = self.mcp_tools.get_all_openai_functions()
            print(f"🔍 Found {len(all_tools)} total MCP tools")
            print(f"🔍 Agent '{agent_type}' allowed tools: {allowed_tools}")

            agent_tools = []

            for tool in all_tools:
                tool_name = tool.get("function", {}).get("name", "")
                tool_category = tool.get("_mcp_tool", "")
                print(f"🔍 Checking tool: {tool_name} (category: {tool_category})")
                # Check if tool belongs to allowed categories
                if tool_category in allowed_tools:
                    print(f"✅ Tool '{tool_name}' matched category '{tool_category}'")
                    agent_tools.append(tool)

            print(f"🔧 Agent '{agent_type}' has access to {len(agent_tools)} tools")
            return agent_tools

        except ImportError as e:
            print(f"❌ ImportError loading agent configs: {e}")
            # Fallback - give access to basic tools
            return self.mcp_tools.get_all_openai_functions()

    async def invoke_agent(self, agent_type: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke a specific agent with a message.
        Returns the full response including content and tools used.
        """
        print(f"🎯 Invoking agent '{agent_type}' with message: {message[:50]}...")

        # Ensure agent is initialized
        await self.initialize_agent(agent_type)

        # Load agent's conversation history
        conversation_history = self.load_agent_memory(agent_type)

        # Add context from other agents if provided
        if context and context.get("from_agent"):
            message = f"Message from {context['from_agent']}: {message}"

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": self.get_agent_system_prompt(agent_type)}
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        # Get agent-specific tools
        tools = self.get_agent_tools(agent_type)

        try:
            # Call OpenAI
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.7
            )

            assistant_message = response.choices[0].message
            response_content = assistant_message.content or ""
            tools_used = []

            # Handle tool calls if any
            if assistant_message.tool_calls:
                print(f"🔧 Agent '{agent_type}' is using {len(assistant_message.tool_calls)} tools")

                # Save the assistant message with tool calls
                self.save_agent_memory(agent_type, {
                    "role": "assistant",
                    "content": response_content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                    "timestamp": datetime.now().isoformat()
                })

                # Execute tools using MCP framework
                if self.mcp_tools:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        try:
                            tool_result = await self.mcp_tools.execute_openai_function(tool_name, tool_args)
                            tools_used.append({
                                "name": tool_name,
                                "arguments": tool_args,
                                "result": tool_result
                            })

                            # Save tool result
                            self.save_agent_memory(agent_type, {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": json.dumps(tool_result),
                                "timestamp": datetime.now().isoformat()
                            })

                        except Exception as e:
                            print(f"❌ Tool execution failed: {tool_name}: {e}")
                            tools_used.append({
                                "name": tool_name,
                                "arguments": tool_args,
                                "error": str(e)
                            })

            else:
                # Save regular assistant message
                self.save_agent_memory(agent_type, {
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat()
                })

            # Save user message
            self.save_agent_memory(agent_type, {
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "content": response_content,
                "tools_used": tools_used,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Agent invocation failed for '{agent_type}': {e}")
            return {
                "content": f"I encountered an error: {str(e)}",
                "tools_used": [],
                "agent_type": agent_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def invoke_agent_streaming(self, agent_type: str, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Invoke agent with streaming response for real-time chat.
        """
        print(f"💬 Streaming invocation for agent '{agent_type}'")

        # Ensure agent is initialized
        await self.initialize_agent(agent_type)

        # Load agent's conversation history
        conversation_history = self.load_agent_memory(agent_type)

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": self.get_agent_system_prompt(agent_type)}
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        # Get agent-specific tools
        tools = self.get_agent_tools(agent_type)

        try:
            # Stream OpenAI response
            response_stream = self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.7,
                stream=True
            )

            # Let MCP framework handle streaming + tool execution
            if self.mcp_tools:
                full_response = ""
                async for chunk in self.mcp_tools.handle_streaming_response(
                    response_stream,
                    save_conversation_callback=lambda content: self.save_agent_memory(agent_type, {
                        "role": "assistant",
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    })
                ):
                    if chunk.get("type") == "content":
                        full_response += chunk.get("content", "")
                    yield chunk

                # Save user message after completion
                self.save_agent_memory(agent_type, {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Fallback streaming without tools
                full_response = ""
                for chunk in response_stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield {"type": "content", "content": content}

                # Save conversation
                self.save_agent_memory(agent_type, {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                })
                self.save_agent_memory(agent_type, {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            error_msg = f"Streaming failed for agent '{agent_type}': {str(e)}"
            print(f"❌ {error_msg}")
            yield {"type": "content", "content": f"I encountered an error: {str(e)}"}

    def get_agent_status(self, agent_type: str) -> Dict[str, Any]:
        """Get status information for a specific agent."""
        agent_path = self.agents_memory_path / agent_type

        if not agent_path.exists():
            return {
                "agent_type": agent_type,
                "status": "not_initialized",
                "conversation_count": 0,
                "last_active": None
            }

        try:
            # Load conversation data
            conversation_file = agent_path / "conversation.json"
            if conversation_file.exists():
                with open(conversation_file, "r") as f:
                    data = json.load(f)

                return {
                    "agent_type": agent_type,
                    "status": "active",
                    "conversation_count": len(data.get("messages", [])),
                    "last_active": data.get("last_active"),
                    "created_at": data.get("created_at")
                }
            else:
                return {
                    "agent_type": agent_type,
                    "status": "initialized",
                    "conversation_count": 0,
                    "last_active": None
                }

        except Exception as e:
            return {
                "agent_type": agent_type,
                "status": "error",
                "error": str(e),
                "conversation_count": 0,
                "last_active": None
            }

    def list_available_agents(self) -> List[str]:
        """List all available agent types."""
        try:
            from agent_configs import AGENT_CONFIGS
            return list(AGENT_CONFIGS.keys())
        except ImportError:
            # Fallback list
            return ["ceo", "frontend", "backend", "design", "testing"]

    def cross_agent_communication(self, from_agent: str, to_agent: str, message: str) -> Dict[str, Any]:
        """Enable communication between agents."""
        context = {
            "from_agent": from_agent,
            "cross_agent_message": True,
            "timestamp": datetime.now().isoformat()
        }

        return self.invoke_agent(to_agent, message, context)