"""
Team Tools MCP - Team communication and message board functionality
Provides tools for agents to communicate with each other through a persistent message board.
Critical for testing persistent memory and cross-agent communication.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp_tools.base_mcp import BaseMCPTool, MCPToolError, openai_function


class TeamToolsMCP(BaseMCPTool):
    """MCP tools for team communication and coordination."""

    def __init__(self, workspace_path: Path, startup_id: str):
        super().__init__(workspace_path, startup_id)
        self.team_board_path = self.workspace / "memory" / "team_chat"
        self.shared_notes_path = self.workspace / "memory" / "shared_notes"

        # Ensure directories exist
        self.team_board_path.mkdir(parents=True, exist_ok=True)
        self.shared_notes_path.mkdir(parents=True, exist_ok=True)

    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute team communication action."""
        action_map = {
            "write_message": self.write_message,
            "read_messages": self.read_messages,
            "write_shared_note": self.write_shared_note,
            "read_shared_note": self.read_shared_note,
            "list_shared_notes": self.list_shared_notes,
            "create_task": self.create_task,
            "list_tasks": self.list_tasks
        }

        if action not in action_map:
            raise MCPToolError(f"Unknown action: {action}")

        return await action_map[action](**kwargs)

    @openai_function("team_write_message", "Write a message to the team message board for other agents to see", {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to post to the team board"
            },
            "author": {
                "type": "string",
                "description": "The agent posting the message (e.g., 'CEO', 'Frontend Agent')"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high", "urgent"],
                "description": "Priority level of the message"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags for categorizing the message"
            }
        },
        "required": ["message", "author"]
    })
    async def write_message(self, message: str, author: str, priority: str = "normal", tags: List[str] = None) -> Dict[str, Any]:
        """Write a message to the team message board."""
        try:
            timestamp = datetime.now().isoformat()
            message_data = {
                "id": f"msg_{int(datetime.now().timestamp())}",
                "message": message,
                "author": author,
                "priority": priority,
                "tags": tags or [],
                "timestamp": timestamp,
                "startup_id": self.startup_id
            }

            # Save to team board file
            board_file = self.team_board_path / "messages.json"

            # Load existing messages
            messages = []
            if board_file.exists():
                with open(board_file, 'r') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])

            # Add new message
            messages.append(message_data)

            # Keep only last 100 messages
            messages = messages[-100:]

            # Save back to file
            with open(board_file, 'w') as f:
                json.dump({
                    "startup_id": self.startup_id,
                    "last_updated": timestamp,
                    "message_count": len(messages),
                    "messages": messages
                }, f, indent=2)

            self.log_activity("team_message_posted", {
                "author": author,
                "priority": priority,
                "message_length": len(message)
            })

            return {
                "success": True,
                "message_id": message_data["id"],
                "timestamp": timestamp,
                "total_messages": len(messages)
            }

        except Exception as e:
            raise MCPToolError(f"Failed to write team message: {str(e)}")

    @openai_function("team_read_messages", "Read messages from the team message board", {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of recent messages to retrieve",
                "default": 10
            },
            "priority_filter": {
                "type": "string",
                "enum": ["low", "normal", "high", "urgent"],
                "description": "Filter messages by priority level"
            },
            "author_filter": {
                "type": "string",
                "description": "Filter messages by author"
            }
        }
    })
    async def read_messages(self, limit: int = 10, priority_filter: str = None, author_filter: str = None) -> Dict[str, Any]:
        """Read messages from the team message board."""
        try:
            board_file = self.team_board_path / "messages.json"

            if not board_file.exists():
                return {
                    "success": True,
                    "messages": [],
                    "total_count": 0,
                    "info": "No messages found on team board"
                }

            with open(board_file, 'r') as f:
                data = json.load(f)
                all_messages = data.get("messages", [])

            # Apply filters
            filtered_messages = all_messages

            if priority_filter:
                filtered_messages = [m for m in filtered_messages if m.get("priority") == priority_filter]

            if author_filter:
                filtered_messages = [m for m in filtered_messages if m.get("author") == author_filter]

            # Get recent messages
            recent_messages = filtered_messages[-limit:] if limit > 0 else filtered_messages

            self.log_activity("team_messages_read", {
                "messages_retrieved": len(recent_messages),
                "filters_applied": {
                    "priority": priority_filter,
                    "author": author_filter
                }
            })

            return {
                "success": True,
                "messages": recent_messages,
                "total_count": len(all_messages),
                "filtered_count": len(filtered_messages)
            }

        except Exception as e:
            raise MCPToolError(f"Failed to read team messages: {str(e)}")

    @openai_function("team_write_shared_note", "Write a shared note for the team", {
        "type": "object",
        "properties": {
            "note_name": {
                "type": "string",
                "description": "Name/identifier for the shared note"
            },
            "content": {
                "type": "string",
                "description": "Content of the shared note"
            },
            "author": {
                "type": "string",
                "description": "The agent creating the note"
            }
        },
        "required": ["note_name", "content", "author"]
    })
    async def write_shared_note(self, note_name: str, content: str, author: str) -> Dict[str, Any]:
        """Write a shared note for team reference."""
        try:
            timestamp = datetime.now().isoformat()
            note_data = {
                "name": note_name,
                "content": content,
                "author": author,
                "created_at": timestamp,
                "updated_at": timestamp,
                "startup_id": self.startup_id
            }

            # Save note file
            note_file = self.shared_notes_path / f"{note_name}.json"
            with open(note_file, 'w') as f:
                json.dump(note_data, f, indent=2)

            self.log_activity("shared_note_created", {
                "note_name": note_name,
                "author": author,
                "content_length": len(content)
            })

            return {
                "success": True,
                "note_name": note_name,
                "timestamp": timestamp
            }

        except Exception as e:
            raise MCPToolError(f"Failed to write shared note: {str(e)}")

    @openai_function("team_read_shared_note", "Read a specific shared note", {
        "type": "object",
        "properties": {
            "note_name": {
                "type": "string",
                "description": "Name of the shared note to read"
            }
        },
        "required": ["note_name"]
    })
    async def read_shared_note(self, note_name: str) -> Dict[str, Any]:
        """Read a specific shared note."""
        try:
            note_file = self.shared_notes_path / f"{note_name}.json"

            if not note_file.exists():
                return {
                    "success": False,
                    "error": f"Shared note '{note_name}' not found"
                }

            with open(note_file, 'r') as f:
                note_data = json.load(f)

            self.log_activity("shared_note_read", {"note_name": note_name})

            return {
                "success": True,
                "note": note_data
            }

        except Exception as e:
            raise MCPToolError(f"Failed to read shared note: {str(e)}")

    @openai_function("team_list_shared_notes", "List all available shared notes", {
        "type": "object",
        "properties": {}
    })
    async def list_shared_notes(self) -> Dict[str, Any]:
        """List all available shared notes."""
        try:
            notes = []
            for note_file in self.shared_notes_path.glob("*.json"):
                try:
                    with open(note_file, 'r') as f:
                        note_data = json.load(f)
                    notes.append({
                        "name": note_data.get("name", note_file.stem),
                        "author": note_data.get("author", "unknown"),
                        "created_at": note_data.get("created_at"),
                        "updated_at": note_data.get("updated_at")
                    })
                except Exception:
                    continue

            self.log_activity("shared_notes_listed", {"notes_count": len(notes)})

            return {
                "success": True,
                "notes": notes,
                "total_count": len(notes)
            }

        except Exception as e:
            raise MCPToolError(f"Failed to list shared notes: {str(e)}")

    @openai_function("team_create_task", "Create a task for team coordination", {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the task"
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the task"
            },
            "assigned_to": {
                "type": "string",
                "description": "Agent assigned to the task"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high", "urgent"],
                "description": "Priority level of the task"
            },
            "due_date": {
                "type": "string",
                "description": "Due date for the task (ISO format)"
            }
        },
        "required": ["title", "description", "assigned_to"]
    })
    async def create_task(self, title: str, description: str, assigned_to: str, priority: str = "normal", due_date: str = None) -> Dict[str, Any]:
        """Create a task for team coordination."""
        try:
            timestamp = datetime.now().isoformat()
            task_id = f"task_{int(datetime.now().timestamp())}"

            task_data = {
                "id": task_id,
                "title": title,
                "description": description,
                "assigned_to": assigned_to,
                "priority": priority,
                "due_date": due_date,
                "status": "pending",
                "created_at": timestamp,
                "updated_at": timestamp,
                "startup_id": self.startup_id
            }

            # Save task file
            tasks_path = self.workspace / "memory" / "tasks"
            tasks_path.mkdir(parents=True, exist_ok=True)
            task_file = tasks_path / f"{task_id}.json"

            with open(task_file, 'w') as f:
                json.dump(task_data, f, indent=2)

            self.log_activity("task_created", {
                "task_id": task_id,
                "assigned_to": assigned_to,
                "priority": priority
            })

            return {
                "success": True,
                "task_id": task_id,
                "timestamp": timestamp
            }

        except Exception as e:
            raise MCPToolError(f"Failed to create task: {str(e)}")

    @openai_function("team_list_tasks", "List all tasks for the team", {
        "type": "object",
        "properties": {
            "assigned_to": {
                "type": "string",
                "description": "Filter tasks by assignee"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed", "cancelled"],
                "description": "Filter tasks by status"
            }
        }
    })
    async def list_tasks(self, assigned_to: str = None, status: str = None) -> Dict[str, Any]:
        """List all tasks for the team."""
        try:
            tasks_path = self.workspace / "memory" / "tasks"
            tasks = []

            if tasks_path.exists():
                for task_file in tasks_path.glob("*.json"):
                    try:
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)

                        # Apply filters
                        if assigned_to and task_data.get("assigned_to") != assigned_to:
                            continue
                        if status and task_data.get("status") != status:
                            continue

                        tasks.append(task_data)
                    except Exception:
                        continue

            self.log_activity("tasks_listed", {
                "tasks_count": len(tasks),
                "filters": {"assigned_to": assigned_to, "status": status}
            })

            return {
                "success": True,
                "tasks": tasks,
                "total_count": len(tasks)
            }

        except Exception as e:
            raise MCPToolError(f"Failed to list tasks: {str(e)}")