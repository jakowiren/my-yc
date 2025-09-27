"""
Base MCP Tool Framework
Provides foundation for all CEO tools with workspace context and safety.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from functools import wraps


class MCPToolError(Exception):
    """Base exception for MCP tool operations."""
    pass


def openai_function(name: str, description: str, parameters: Optional[Dict[str, Any]] = None):
    """
    Decorator to auto-register MCP methods as OpenAI functions.

    Usage:
        @openai_function("get_project_overview", "Get project overview")
        async def get_project_overview(self): ...
    """
    def decorator(func: Callable) -> Callable:
        # Store OpenAI function metadata on the function
        func._openai_function = {
            "name": name,
            "description": description,
            "parameters": parameters or {"type": "object", "properties": {}},
            "method": func.__name__
        }
        return func
    return decorator


class WorkspaceSecurityError(MCPToolError):
    """Raised when operation violates workspace boundaries."""
    pass


class BaseMCPTool(ABC):
    """
    Base class for all MCP tools with workspace context and safety.

    All tools operate within startup-specific workspaces and provide
    logging, error handling, and security boundaries.
    """

    def __init__(self, workspace_path: Path, startup_id: str):
        """Initialize tool with workspace context."""
        self.workspace = Path(workspace_path)
        self.startup_id = startup_id
        self.github_repo_path = self.workspace / "github_repo"
        self.tools_path = self.workspace / "tools"
        self.memory_path = self.workspace / "memory"
        self.docs_path = self.workspace / "docs"

        # Ensure required directories exist
        self._ensure_workspace_structure()

    def _ensure_workspace_structure(self):
        """Ensure all required workspace directories exist."""
        required_dirs = [
            self.tools_path,
            self.tools_path / "logs",
            self.docs_path,
            self.memory_path / "ceo",
            self.memory_path / "shared"
        ]

        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, path: str) -> Path:
        """
        Validate that a path is within workspace boundaries.

        Args:
            path: Path to validate (can be relative or absolute)

        Returns:
            Resolved Path object within workspace

        Raises:
            WorkspaceSecurityError: If path is outside workspace
        """
        if os.path.isabs(path):
            resolved_path = Path(path)
        else:
            resolved_path = self.workspace / path

        # Resolve to handle .. and . components
        resolved_path = resolved_path.resolve()

        # Check if path is within workspace
        try:
            resolved_path.relative_to(self.workspace.resolve())
            return resolved_path
        except ValueError:
            raise WorkspaceSecurityError(
                f"Path '{path}' is outside workspace boundaries"
            )

    def log_activity(self, activity_type: str, details: Dict[str, Any], level: str = "info"):
        """
        Log tool activity for debugging and coordination.

        Args:
            activity_type: Type of activity (e.g., "file_read", "git_commit")
            details: Activity-specific details
            level: Log level ("info", "warning", "error")
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "startup_id": self.startup_id,
            "tool": self.__class__.__name__,
            "activity": activity_type,
            "level": level,
            "details": details
        }

        # Write to tool-specific log
        log_file = self.tools_path / "logs" / f"{self.__class__.__name__.lower()}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also write to main activity log
        main_log = self.memory_path / "shared" / "activity.jsonl"
        with open(main_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute tool action with full error handling and logging.

        Args:
            action: Action to execute
            **kwargs: Action-specific parameters

        Returns:
            Result dictionary with success status and data
        """
        start_time = datetime.now()

        try:
            # Log action start
            self.log_activity("action_start", {
                "action": action,
                "parameters": kwargs
            })

            # Execute the action
            result = await self._execute_action(action, **kwargs)

            # Log successful completion
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_activity("action_complete", {
                "action": action,
                "execution_time_seconds": execution_time,
                "success": True
            })

            return {
                "success": True,
                "action": action,
                "result": result,
                "execution_time": execution_time
            }

        except Exception as e:
            # Log error
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_activity("action_error", {
                "action": action,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time_seconds": execution_time
            }, level="error")

            return {
                "success": False,
                "action": action,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time
            }

    @abstractmethod
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """
        Execute the specific action. Implemented by subclasses.

        Args:
            action: Action to execute
            **kwargs: Action-specific parameters

        Returns:
            Action result
        """
        pass

    def get_available_actions(self) -> List[str]:
        """Get list of available actions for this tool."""
        # Default implementation returns methods that don't start with _
        actions = []
        for attr_name in dir(self):
            if not attr_name.startswith('_') and callable(getattr(self, attr_name)):
                if attr_name not in ['execute', 'log_activity', 'get_available_actions']:
                    actions.append(attr_name)
        return actions

    def get_workspace_status(self) -> Dict[str, Any]:
        """Get current workspace status and health."""
        return {
            "startup_id": self.startup_id,
            "workspace_path": str(self.workspace),
            "github_repo_exists": self.github_repo_path.exists(),
            "structure_valid": all([
                self.tools_path.exists(),
                self.memory_path.exists(),
                self.docs_path.exists()
            ]),
            "total_files": len(list(self.workspace.rglob("*"))) if self.workspace.exists() else 0
        }


class MCPToolRegistry:
    """
    Registry for managing multiple MCP tools for a CEO agent.
    """

    def __init__(self, workspace_path: Path, startup_id: str):
        """Initialize tool registry."""
        self.workspace_path = workspace_path
        self.startup_id = startup_id
        self.tools: Dict[str, BaseMCPTool] = {}

    def register_tool(self, name: str, tool_class, **kwargs):
        """Register a tool instance."""
        tool = tool_class(self.workspace_path, self.startup_id, **kwargs)
        self.tools[name] = tool
        return tool

    async def execute_tool(self, tool_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Execute action on specified tool."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }

        return await self.tools[tool_name].execute(action, **kwargs)

    def get_all_openai_functions(self) -> List[Dict[str, Any]]:
        """
        Auto-discover all OpenAI functions from registered tools.
        Returns list ready for OpenAI API.
        """
        functions = []

        for tool_name, tool in self.tools.items():
            # Get all methods with @openai_function decorator
            for method_name in dir(tool):
                method = getattr(tool, method_name)
                if hasattr(method, '_openai_function'):
                    func_def = method._openai_function
                    functions.append({
                        "type": "function",
                        "function": {
                            "name": func_def["name"],
                            "description": func_def["description"],
                            "parameters": func_def["parameters"]
                        },
                        "_mcp_tool": tool_name,  # Internal routing info
                        "_mcp_method": func_def["method"]
                    })

        return functions

    async def execute_openai_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute OpenAI function call by routing to appropriate MCP tool.
        """
        # Find the function definition
        for tool_name, tool in self.tools.items():
            for method_name in dir(tool):
                method = getattr(tool, method_name)
                if hasattr(method, '_openai_function'):
                    if method._openai_function["name"] == function_name:
                        try:
                            # Call the method with arguments
                            result = await method(**arguments)
                            return {"success": True, "result": result}
                        except Exception as e:
                            return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Function '{function_name}' not found"}

    async def handle_streaming_response(self, openai_stream, save_conversation_callback=None):
        """
        Handle OpenAI streaming response with automatic tool execution.
        Yields content chunks and handles function calls transparently.
        """
        content_chunks = []
        tool_calls = []

        # Collect streaming chunks and tool calls
        for chunk in openai_stream:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                # Yield content immediately for streaming
                if delta.content:
                    content_chunks.append(delta.content)
                    yield {"type": "content", "content": delta.content}

                # Collect tool calls
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        # Handle incremental tool call building
                        if len(tool_calls) <= tool_call.index:
                            tool_calls.extend([None] * (tool_call.index + 1 - len(tool_calls)))

                        if tool_calls[tool_call.index] is None:
                            tool_calls[tool_call.index] = {
                                "id": tool_call.id,
                                "function": {"name": "", "arguments": ""}
                            }

                        if tool_call.function:
                            if tool_call.function.name:
                                tool_calls[tool_call.index]["function"]["name"] += tool_call.function.name
                            if tool_call.function.arguments:
                                tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

        # Execute tool calls if any
        if tool_calls and any(tc for tc in tool_calls if tc):
            yield {"type": "tool_start", "content": ""}

            for tool_call in tool_calls:
                if tool_call:
                    function_name = tool_call["function"]["name"]
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}

                    yield {"type": "tool_execution", "content": f"Using {function_name}..."}

                    # Execute via auto-routing
                    result = await self.execute_openai_function(function_name, arguments)

                    if not result["success"]:
                        yield {"type": "tool_error", "content": f"Tool error: {result.get('error')}"}

        # Save full content for conversation saving
        full_content = "".join(content_chunks)
        if save_conversation_callback:
            save_conversation_callback(full_content)

    def get_all_tools_status(self) -> Dict[str, Any]:
        """Get status of all registered tools."""
        return {
            tool_name: tool.get_workspace_status()
            for tool_name, tool in self.tools.items()
        }

    def get_available_actions(self) -> Dict[str, List[str]]:
        """Get available actions for all tools."""
        return {
            tool_name: tool.get_available_actions()
            for tool_name, tool in self.tools.items()
        }