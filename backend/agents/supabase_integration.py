"""
Supabase Integration for Real-Time Logging
Enables Modal agents to stream logs directly to Supabase for frontend monitoring.
"""

import os
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional


class SupabaseLogger:
    """Real-time logging to Supabase for live frontend monitoring."""

    def __init__(self, project_id: str):
        """
        Initialize Supabase logger.

        Args:
            project_id: Project UUID for log filtering
        """
        self.project_id = project_id
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")  # or SERVICE_ROLE_KEY for server-side

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

        self.headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "apikey": self.supabase_key
        }

    async def log(
        self,
        agent_name: str,
        message: str,
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send log entry to Supabase for real-time frontend updates.

        Args:
            agent_name: Name of the agent sending the log
            message: Log message text
            level: Log level ('info', 'success', 'warning', 'error')
            data: Additional structured data

        Returns:
            True if log was sent successfully, False otherwise
        """
        try:
            log_entry = {
                "project_id": self.project_id,
                "agent_name": agent_name,
                "level": level,
                "message": message,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/project_logs",
                    headers=self.headers,
                    json=log_entry
                )

                if response.status_code in [200, 201]:
                    return True
                else:
                    print(f"Failed to log to Supabase: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
            return False

    async def update_project_status(
        self,
        status: str,
        progress: Optional[int] = None,
        github_url: Optional[str] = None,
        deployment_url: Optional[str] = None
    ) -> bool:
        """
        Update project status in Supabase.

        Args:
            status: Project status ('spawning', 'running', 'completed', 'failed')
            progress: Completion percentage (0-100)
            github_url: GitHub repository URL
            deployment_url: Deployment URL (Vercel, etc.)

        Returns:
            True if update was successful, False otherwise
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }

            if progress is not None:
                update_data["progress"] = progress
            if github_url:
                update_data["github_url"] = github_url
            if deployment_url:
                update_data["deployment_url"] = deployment_url

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.patch(
                    f"{self.supabase_url}/rest/v1/projects?id=eq.{self.project_id}",
                    headers=self.headers,
                    json=update_data
                )

                if response.status_code == 204:  # Supabase PATCH returns 204 No Content
                    return True
                else:
                    print(f"Failed to update project status: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"Error updating project status: {str(e)}")
            return False

    async def log_info(self, agent_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log info-level message."""
        return await self.log(agent_name, message, "info", data)

    async def log_success(self, agent_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log success-level message."""
        return await self.log(agent_name, message, "success", data)

    async def log_warning(self, agent_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning-level message."""
        return await self.log(agent_name, message, "warning", data)

    async def log_error(self, agent_name: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log error-level message."""
        return await self.log(agent_name, message, "error", data)


# Utility function for agents
async def create_supabase_logger(project_id: str) -> Optional[SupabaseLogger]:
    """
    Create a Supabase logger instance with error handling.

    Args:
        project_id: Project UUID

    Returns:
        SupabaseLogger instance or None if configuration is invalid
    """
    try:
        return SupabaseLogger(project_id)
    except ValueError as e:
        print(f"Cannot create Supabase logger: {e}")
        return None