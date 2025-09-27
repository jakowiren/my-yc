"""
Workspace Manager - Handles persistent workspace creation and management for startups
Each startup gets its own workspace with memory, files, and team coordination structures.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class WorkspaceManager:
    """Manages persistent workspaces for AI agent teams."""

    def __init__(self, base_workspace_path: str = "/workspace"):
        self.base_path = Path(base_workspace_path)

    def get_workspace_path(self, startup_id: str) -> Path:
        """Get the workspace path for a specific startup."""
        return self.base_path / startup_id

    def initialize_workspace(self, startup_id: str, startup_name: str, design_doc: Dict[str, Any]) -> Path:
        """
        Initialize complete workspace structure for a new startup.

        Args:
            startup_id: Unique identifier for the startup
            startup_name: Human-readable startup name
            design_doc: Design document from Jason AI

        Returns:
            Path to the initialized workspace
        """
        workspace = self.get_workspace_path(startup_id)

        print(f"🏗️ Initializing workspace for '{startup_name}' at {workspace}")

        # Create main directory structure
        self._create_directory_structure(workspace)

        # Initialize CEO memory and identity
        self._initialize_ceo_memory(workspace, startup_name, design_doc)

        # Create team coordination structure
        self._initialize_team_structure(workspace)

        # Initialize project metadata
        self._initialize_project_metadata(workspace, startup_id, startup_name, design_doc)

        print(f"✅ Workspace initialized successfully")
        return workspace

    def _create_directory_structure(self, workspace: Path):
        """Create the complete directory structure for a startup workspace."""

        directories = [
            # Core workspace
            workspace,

            # GitHub repository (cloned repo will go here)
            workspace / "github_repo",

            # Documentation and project files
            workspace / "docs",
            workspace / "data",

            # Memory structure for all agents
            workspace / "memory",
            workspace / "memory" / "ceo",
            workspace / "memory" / "agents",
            workspace / "memory" / "team_chat",

            # MCP configuration
            workspace / "mcp"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _initialize_ceo_memory(self, workspace: Path, startup_name: str, design_doc: Dict[str, Any]):
        """Initialize CEO identity and memory structures."""

        ceo_memory = workspace / "memory" / "ceo"

        # CEO Identity
        identity = {
            "role": "CEO",
            "startup_name": startup_name,
            "personality": "Strategic, decisive, founder-focused, autonomous",
            "responsibilities": [
                "Strategic planning and decision making",
                "Team coordination and management",
                "Founder communication and updates",
                "Project oversight and quality assurance"
            ],
            "communication_style": "Professional yet approachable, data-driven",
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(ceo_memory / "identity.json", "w") as f:
            json.dump(identity, f, indent=2)

        # Initial state
        initial_state = {
            "conversations": [],
            "decisions": [],
            "team_plan": None,
            "current_focus": "Project initialization and team planning",
            "last_active": datetime.now().isoformat(),
            "status": "initialized"
        }

        with open(ceo_memory / "state.json", "w") as f:
            json.dump(initial_state, f, indent=2)

        # Strategic context from design document
        strategic_context = {
            "design_document": design_doc,
            "key_insights": [],
            "strategic_decisions": [],
            "success_metrics": design_doc.get("success_metrics", []),
            "target_market": design_doc.get("target_market", ""),
            "value_proposition": design_doc.get("value_proposition", "")
        }

        with open(ceo_memory / "strategic_context.json", "w") as f:
            json.dump(strategic_context, f, indent=2)

        # Create empty conversation log
        (ceo_memory / "conversations.jsonl").touch()

        # Create decisions log
        with open(ceo_memory / "decisions.md", "w") as f:
            f.write(f"# Strategic Decisions for {startup_name}\n\n")
            f.write(f"CEO initialized on {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## Key Decisions\n\n")
            f.write("*Decisions will be logged here as the CEO makes them*\n")

    def _initialize_team_structure(self, workspace: Path):
        """Initialize team coordination and communication structures."""

        team_chat_dir = workspace / "memory" / "team_chat"

        # Team chat channels
        channels = ["general", "dev-updates", "ceo-announcements", "task-coordination"]

        for channel in channels:
            (team_chat_dir / f"{channel}.jsonl").touch()

        # Team configuration
        team_config = {
            "communication_channels": channels,
            "agent_types": [
                "Frontend Agent",
                "Backend Agent",
                "Database Agent",
                "Testing Agent",
                "DevOps Agent",
                "Content Agent",
                "Design Agent"
            ],
            "coordination_rules": {
                "daily_standup": "09:00 UTC",
                "progress_updates": "Every 4 hours",
                "code_review": "Before any commit",
                "ceo_reports": "Daily summary"
            },
            "created_at": datetime.now().isoformat()
        }

        with open(team_chat_dir / "team_config.json", "w") as f:
            json.dump(team_config, f, indent=2)

        # Initialize task queue
        task_queue = {
            "pending": [],
            "in_progress": [],
            "completed": [],
            "blocked": []
        }

        with open(workspace / "memory" / "task_queue.json", "w") as f:
            json.dump(task_queue, f, indent=2)

    def _initialize_project_metadata(self, workspace: Path, startup_id: str, startup_name: str, design_doc: Dict[str, Any]):
        """Initialize project-level metadata and configuration."""

        project_metadata = {
            "startup_id": startup_id,
            "startup_name": startup_name,
            "workspace_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "design_document": design_doc,
            "workspace_structure": {
                "github_repo": "Cloned GitHub repository",
                "docs": "Project documentation",
                "data": "Configuration and data files",
                "memory/ceo": "CEO agent memory and state",
                "memory/agents": "Individual agent memories",
                "memory/team_chat": "Team communication logs",
                "mcp": "MCP tool configurations"
            },
            "status": "initialized"
        }

        with open(workspace / "project_metadata.json", "w") as f:
            json.dump(project_metadata, f, indent=2)

        # Create MCP configuration placeholder
        mcp_config = {
            "version": "1.0",
            "tools": {
                "file_operations": True,
                "git_operations": True,
                "terminal_access": True,
                "github_api": True
            },
            "workspace_path": str(workspace),
            "github_repo_path": str(workspace / "github_repo"),
            "restrictions": [
                "No operations outside workspace",
                "All changes must be logged",
                "Destructive operations require confirmation"
            ]
        }

        with open(workspace / "mcp" / "config.json", "w") as f:
            json.dump(mcp_config, f, indent=2)

    def workspace_exists(self, startup_id: str) -> bool:
        """Check if workspace already exists for a startup."""
        workspace = self.get_workspace_path(startup_id)
        return workspace.exists() and (workspace / "project_metadata.json").exists()

    def get_workspace_info(self, startup_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace information for a startup."""
        if not self.workspace_exists(startup_id):
            return None

        workspace = self.get_workspace_path(startup_id)

        try:
            with open(workspace / "project_metadata.json", "r") as f:
                metadata = json.load(f)

            with open(workspace / "memory" / "ceo" / "state.json", "r") as f:
                ceo_state = json.load(f)

            return {
                "workspace_path": str(workspace),
                "metadata": metadata,
                "ceo_status": ceo_state.get("status", "unknown"),
                "last_activity": ceo_state.get("last_active"),
                "conversation_count": len(ceo_state.get("conversations", [])),
                "team_plan_exists": ceo_state.get("team_plan") is not None
            }

        except Exception as e:
            print(f"❌ Error reading workspace info: {e}")
            return None

    def update_last_activity(self, startup_id: str):
        """Update the last activity timestamp for a workspace."""
        if not self.workspace_exists(startup_id):
            return

        workspace = self.get_workspace_path(startup_id)

        # Update project metadata
        try:
            metadata_file = workspace / "project_metadata.json"
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            metadata["last_updated"] = datetime.now().isoformat()

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to update workspace activity: {e}")

    def cleanup_workspace(self, startup_id: str) -> bool:
        """
        Clean up workspace for a startup.
        WARNING: This will delete all persistent data!
        """
        workspace = self.get_workspace_path(startup_id)

        if not workspace.exists():
            return True

        try:
            import shutil
            shutil.rmtree(workspace)
            print(f"🗑️ Workspace cleaned up for startup {startup_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to cleanup workspace: {e}")
            return False


# Global workspace manager instance
workspace_manager = WorkspaceManager()


def get_workspace_manager() -> WorkspaceManager:
    """Get the global workspace manager instance."""
    return workspace_manager