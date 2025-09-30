"""
Git MCP Tools
CEO-focused git operations for understanding project history and making strategic commits.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from mcp_tools.base_mcp import BaseMCPTool, MCPToolError, openai_function


class GitMCP(BaseMCPTool):
    """
    Git operations for CEO strategic oversight.

    Focus: Understanding project history, making documentation commits,
    basic repository health checks. Complex git operations left for specialist agents.
    """

    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute git action."""
        action_map = {
            "clone_repository": self.clone_repository,
            "get_status": self.get_status,
            "get_history": self.get_history,
            "get_recent_changes": self.get_recent_changes,
            "commit_changes": self.commit_changes,
            "push_changes": self.push_changes,
            "get_repository_info": self.get_repository_info,
            "check_repository_health": self.check_repository_health,
            "get_branch_info": self.get_branch_info,
            "create_branch": self.create_branch
        }

        if action not in action_map:
            raise MCPToolError(f"Unknown action: {action}")

        return await action_map[action](**kwargs)

    @openai_function("clone_repository", "Clone a GitHub repository to the workspace", {
        "type": "object",
        "properties": {
            "repo_url": {"type": "string", "description": "GitHub repository URL to clone"},
            "branch": {"type": "string", "description": "Specific branch to clone (optional)"}
        },
        "required": ["repo_url"]
    })
    async def clone_repository(self, repo_url: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Clone GitHub repository into workspace.

        Args:
            repo_url: Repository URL to clone
            branch: Specific branch to clone (default: main)

        Returns:
            Clone operation result
        """
        try:
            # Ensure github_repo directory exists and is empty
            if self.github_repo_path.exists():
                # Remove existing content
                import shutil
                shutil.rmtree(self.github_repo_path)

            self.github_repo_path.mkdir(parents=True)

            # Build git clone command
            cmd = ["git", "clone"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([repo_url, str(self.github_repo_path)])

            # Execute clone
            result = await self._run_git_command(cmd, cwd=self.workspace)

            if result["success"]:
                # Get initial repository info
                repo_info = await self.get_repository_info()

                self.log_activity("repository_cloned", {
                    "repo_url": repo_url,
                    "branch": branch or "default",
                    "clone_path": str(self.github_repo_path)
                })

                return {
                    "repo_url": repo_url,
                    "clone_path": str(self.github_repo_path),
                    "branch": branch or "main",
                    "repository_info": repo_info
                }
            else:
                raise MCPToolError(f"Failed to clone repository: {result['error']}")

        except Exception as e:
            self.log_activity("clone_error", {"repo_url": repo_url, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to clone repository: {str(e)}")

    @openai_function("get_git_status", "Get current git repository status including uncommitted changes")
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current git repository status.

        Returns:
            Repository status including changes, branch info
        """
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            # Get status
            status_result = await self._run_git_command(["git", "status", "--porcelain"],
                                                      cwd=self.github_repo_path)

            # Get current branch
            branch_result = await self._run_git_command(["git", "branch", "--show-current"],
                                                      cwd=self.github_repo_path)

            # Parse status output
            changes = self._parse_git_status(status_result["output"] if status_result["success"] else "")

            return {
                "current_branch": branch_result["output"].strip() if branch_result["success"] else "unknown",
                "clean": len(changes) == 0,
                "changes": changes,
                "total_changes": len(changes)
            }

        except Exception as e:
            self.log_activity("get_status_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get git status: {str(e)}")

    @openai_function("get_git_history", "Get git commit history with optional filtering", {
        "type": "object",
        "properties": {
            "max_commits": {"type": "integer", "description": "Maximum number of commits to return", "default": 10},
            "since_days": {"type": "integer", "description": "Only show commits from the last N days"}
        }
    })
    async def get_history(self, max_commits: int = 10, since_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get commit history for CEO understanding.

        Args:
            max_commits: Maximum number of commits to return
            since_days: Only show commits from last N days

        Returns:
            Commit history with analysis
        """
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            # Build git log command
            cmd = ["git", "log", f"--max-count={max_commits}",
                   "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]

            if since_days:
                cmd.extend([f"--since={since_days} days ago"])

            result = await self._run_git_command(cmd, cwd=self.github_repo_path)

            if not result["success"]:
                return {"error": f"Failed to get git history: {result['error']}"}

            # Parse commit history
            commits = []
            for line in result["output"].strip().split('\n'):
                if not line:
                    continue

                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0][:8],  # Short hash
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

            # Analyze commit patterns
            analysis = self._analyze_commit_history(commits)

            return {
                "commits": commits,
                "total_commits": len(commits),
                "analysis": analysis
            }

        except Exception as e:
            self.log_activity("get_history_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get git history: {str(e)}")

    async def get_recent_changes(self, since_hours: int = 24) -> Dict[str, Any]:
        """
        Get recent changes for status updates.

        Args:
            since_hours: Show changes from last N hours

        Returns:
            Recent changes with file details
        """
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            # Get recent commits
            cmd = ["git", "log", f"--since={since_hours} hours ago",
                   "--pretty=format:%H|%an|%ad|%s", "--date=relative"]

            result = await self._run_git_command(cmd, cwd=self.github_repo_path)

            changes = []
            if result["success"] and result["output"].strip():
                for line in result["output"].strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) == 4:
                            # Get files changed in this commit
                            files_cmd = ["git", "show", "--name-only", "--pretty=format:", parts[0]]
                            files_result = await self._run_git_command(files_cmd, cwd=self.github_repo_path)

                            changed_files = []
                            if files_result["success"]:
                                changed_files = [f for f in files_result["output"].split('\n') if f.strip()]

                            changes.append({
                                "hash": parts[0][:8],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3],
                                "files_changed": changed_files
                            })

            return {
                "since_hours": since_hours,
                "recent_changes": changes,
                "total_changes": len(changes),
                "has_activity": len(changes) > 0
            }

        except Exception as e:
            self.log_activity("get_recent_changes_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get recent changes: {str(e)}")

    @openai_function("commit_changes", "Commit changes to the git repository", {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Commit message"},
            "files": {"type": "array", "items": {"type": "string"}, "description": "Specific files to commit (optional, commits all changes if not specified)"}
        },
        "required": ["message"]
    })
    async def commit_changes(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Commit changes (primarily for documentation and strategic updates).

        Args:
            message: Commit message
            files: Specific files to commit (None = commit all changes)

        Returns:
            Commit operation result
        """
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            # Configure git user if not set
            await self._ensure_git_config()

            # Add files
            if files:
                for file_path in files:
                    add_result = await self._run_git_command(["git", "add", file_path],
                                                           cwd=self.github_repo_path)
                    if not add_result["success"]:
                        return {"error": f"Failed to add file {file_path}: {add_result['error']}"}
            else:
                # Add all changes
                add_result = await self._run_git_command(["git", "add", "."],
                                                       cwd=self.github_repo_path)
                if not add_result["success"]:
                    return {"error": f"Failed to add changes: {add_result['error']}"}

            # Check if there are changes to commit
            status_result = await self._run_git_command(["git", "status", "--porcelain", "--cached"],
                                                      cwd=self.github_repo_path)

            if not status_result["output"].strip():
                return {"error": "No changes to commit"}

            # Commit changes
            commit_result = await self._run_git_command(["git", "commit", "-m", message],
                                                      cwd=self.github_repo_path)

            if commit_result["success"]:
                # Get commit hash
                hash_result = await self._run_git_command(["git", "rev-parse", "HEAD"],
                                                        cwd=self.github_repo_path)
                commit_hash = hash_result["output"].strip()[:8] if hash_result["success"] else "unknown"

                self.log_activity("changes_committed", {
                    "message": message,
                    "files": files or "all",
                    "commit_hash": commit_hash
                })

                return {
                    "success": True,
                    "message": message,
                    "commit_hash": commit_hash,
                    "files_committed": files or "all_changes"
                }
            else:
                return {"error": f"Failed to commit: {commit_result['error']}"}

        except Exception as e:
            self.log_activity("commit_error", {"message": message, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to commit changes: {str(e)}")

    async def push_changes(self, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Push committed changes to remote repository.

        Args:
            branch: Branch to push (None = current branch)

        Returns:
            Push operation result
        """
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            # Get current branch if not specified
            if not branch:
                branch_result = await self._run_git_command(["git", "branch", "--show-current"],
                                                          cwd=self.github_repo_path)
                branch = branch_result["output"].strip() if branch_result["success"] else "main"

            # Push changes
            push_result = await self._run_git_command(["git", "push", "origin", branch],
                                                    cwd=self.github_repo_path)

            if push_result["success"]:
                self.log_activity("changes_pushed", {"branch": branch})

                return {
                    "success": True,
                    "branch": branch,
                    "message": "Changes pushed successfully"
                }
            else:
                return {"error": f"Failed to push: {push_result['error']}"}

        except Exception as e:
            self.log_activity("push_error", {"branch": branch, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to push changes: {str(e)}")

    @openai_function("get_repository_info", "Get comprehensive repository information and metrics")
    async def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information."""
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found"}

            info = {}

            # Get remote URL
            remote_result = await self._run_git_command(["git", "remote", "get-url", "origin"],
                                                      cwd=self.github_repo_path)
            info["remote_url"] = remote_result["output"].strip() if remote_result["success"] else "unknown"

            # Get current branch
            branch_result = await self._run_git_command(["git", "branch", "--show-current"],
                                                      cwd=self.github_repo_path)
            info["current_branch"] = branch_result["output"].strip() if branch_result["success"] else "unknown"

            # Get total commits
            count_result = await self._run_git_command(["git", "rev-list", "--count", "HEAD"],
                                                     cwd=self.github_repo_path)
            info["total_commits"] = int(count_result["output"].strip()) if count_result["success"] else 0

            # Get last commit info
            last_commit_result = await self._run_git_command(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ad|%s", "--date=relative"],
                cwd=self.github_repo_path
            )

            if last_commit_result["success"] and last_commit_result["output"]:
                parts = last_commit_result["output"].split('|', 3)
                if len(parts) == 4:
                    info["last_commit"] = {
                        "hash": parts[0][:8],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    }

            return info

        except Exception as e:
            self.log_activity("get_repo_info_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get repository info: {str(e)}")

    async def check_repository_health(self) -> Dict[str, Any]:
        """Check repository health for CEO oversight."""
        try:
            if not await self._is_git_repo():
                return {"error": "No git repository found", "health": "unhealthy"}

            health_checks = {}

            # Check if repository is clean
            status = await self.get_status()
            health_checks["clean_working_directory"] = status.get("clean", False)

            # Check if connected to remote
            remote_result = await self._run_git_command(["git", "remote", "-v"],
                                                      cwd=self.github_repo_path)
            health_checks["has_remote"] = bool(remote_result["success"] and remote_result["output"])

            # Check recent activity
            recent_changes = await self.get_recent_changes(since_hours=168)  # Last week
            health_checks["recent_activity"] = recent_changes.get("has_activity", False)

            # Check if ahead/behind remote
            fetch_result = await self._run_git_command(["git", "fetch"], cwd=self.github_repo_path)
            if fetch_result["success"]:
                status_result = await self._run_git_command(["git", "status", "-b", "--porcelain"],
                                                          cwd=self.github_repo_path)
                if status_result["success"]:
                    first_line = status_result["output"].split('\n')[0] if status_result["output"] else ""
                    health_checks["in_sync_with_remote"] = "ahead" not in first_line and "behind" not in first_line

            # Overall health assessment
            health_score = sum(health_checks.values())
            total_checks = len(health_checks)

            if health_score == total_checks:
                overall_health = "excellent"
            elif health_score >= total_checks * 0.8:
                overall_health = "good"
            elif health_score >= total_checks * 0.5:
                overall_health = "fair"
            else:
                overall_health = "poor"

            return {
                "overall_health": overall_health,
                "health_score": f"{health_score}/{total_checks}",
                "checks": health_checks,
                "recommendations": self._get_health_recommendations(health_checks)
            }

        except Exception as e:
            self.log_activity("health_check_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to check repository health: {str(e)}")

    # Helper methods

    async def _is_git_repo(self) -> bool:
        """Check if github_repo directory is a git repository."""
        git_dir = self.github_repo_path / ".git"
        return git_dir.exists()

    async def _run_git_command(self, cmd: List[str], cwd: Path) -> Dict[str, Any]:
        """Run git command and return result."""
        try:
            process = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr,
                "return_code": process.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1
            }

    async def _ensure_git_config(self):
        """Ensure git is configured for commits."""
        # Check if user.name is set
        name_result = await self._run_git_command(["git", "config", "user.name"],
                                                cwd=self.github_repo_path)

        if not name_result["success"] or not name_result["output"].strip():
            await self._run_git_command(["git", "config", "user.name", "CEO Agent"],
                                      cwd=self.github_repo_path)

        # Check if user.email is set
        email_result = await self._run_git_command(["git", "config", "user.email"],
                                                 cwd=self.github_repo_path)

        if not email_result["success"] or not email_result["output"].strip():
            await self._run_git_command(["git", "config", "user.email", "ceo@my-yc.com"],
                                      cwd=self.github_repo_path)

    def _parse_git_status(self, status_output: str) -> List[Dict[str, Any]]:
        """Parse git status --porcelain output."""
        changes = []

        for line in status_output.strip().split('\n'):
            if not line:
                continue

            status_code = line[:2]
            file_path = line[3:]

            change_type = "unknown"
            if status_code[0] == 'M' or status_code[1] == 'M':
                change_type = "modified"
            elif status_code[0] == 'A' or status_code[1] == 'A':
                change_type = "added"
            elif status_code[0] == 'D' or status_code[1] == 'D':
                change_type = "deleted"
            elif status_code[0] == '?' and status_code[1] == '?':
                change_type = "untracked"

            changes.append({
                "file": file_path,
                "type": change_type,
                "staged": status_code[0] != ' ' and status_code[0] != '?'
            })

        return changes

    def _analyze_commit_history(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze commit history for patterns."""
        if not commits:
            return {"activity_level": "none"}

        # Count commits by author
        authors = {}
        for commit in commits:
            author = commit["author"]
            authors[author] = authors.get(author, 0) + 1

        # Analyze commit messages for patterns
        message_patterns = {
            "feat": 0,
            "fix": 0,
            "docs": 0,
            "refactor": 0,
            "test": 0
        }

        for commit in commits:
            message = commit["message"].lower()
            for pattern in message_patterns:
                if pattern in message:
                    message_patterns[pattern] += 1

        return {
            "activity_level": "high" if len(commits) > 5 else "moderate" if len(commits) > 2 else "low",
            "primary_contributors": list(authors.keys())[:3],
            "commit_types": message_patterns,
            "most_recent": commits[0]["date"] if commits else None
        }

    def _get_health_recommendations(self, health_checks: Dict[str, bool]) -> List[str]:
        """Get recommendations based on health checks."""
        recommendations = []

        if not health_checks.get("clean_working_directory", True):
            recommendations.append("Consider committing or stashing uncommitted changes")

        if not health_checks.get("has_remote", True):
            recommendations.append("Repository not connected to remote - add origin remote")

        if not health_checks.get("recent_activity", True):
            recommendations.append("No recent activity - consider project status review")

        if not health_checks.get("in_sync_with_remote", True):
            recommendations.append("Repository may be out of sync with remote - consider pull/push")

        return recommendations