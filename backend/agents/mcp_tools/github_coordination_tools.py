"""
GitHub Coordination MCP Tools
CEO-focused GitHub operations for task management and project coordination.
"""

import os
from typing import Dict, Any, List, Optional
from github import Github
from .base_mcp import BaseMCPTool, MCPToolError


class GitHubCoordinationMCP(BaseMCPTool):
    """
    GitHub coordination tools for CEO project management.

    Focus: Creating issues, managing project boards, repository settings,
    coordinating work with GitHub as the central hub.
    """

    def __init__(self, workspace_path, startup_id: str, github_token: Optional[str] = None):
        """Initialize GitHub coordination tools."""
        super().__init__(workspace_path, startup_id)

        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise MCPToolError("GitHub token is required. Set GITHUB_TOKEN environment variable.")

        self.client = Github(self.github_token)
        self.user = self.client.get_user()
        self.repo = None  # Will be set when repo URL is provided

    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute GitHub coordination action."""
        action_map = {
            "set_repository": self.set_repository,
            "create_issue": self.create_issue,
            "list_issues": self.list_issues,
            "update_issue": self.update_issue,
            "create_milestone": self.create_milestone,
            "list_milestones": self.list_milestones,
            "update_repository_settings": self.update_repository_settings,
            "create_project_board": self.create_project_board,
            "add_repository_topics": self.add_repository_topics,
            "create_release": self.create_release,
            "get_repository_insights": self.get_repository_insights,
            "setup_issue_templates": self.setup_issue_templates,
            "create_pull_request": self.create_pull_request
        }

        if action not in action_map:
            raise MCPToolError(f"Unknown action: {action}")

        return await action_map[action](**kwargs)

    async def set_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Set the GitHub repository to work with.

        Args:
            repo_url: GitHub repository URL or owner/repo format

        Returns:
            Repository connection result
        """
        try:
            # Extract owner/repo from URL or use as-is
            if repo_url.startswith("https://github.com/"):
                repo_path = repo_url.replace("https://github.com/", "").replace(".git", "")
            else:
                repo_path = repo_url

            # Get repository
            self.repo = self.client.get_repo(repo_path)

            self.log_activity("repository_connected", {
                "repo_name": self.repo.full_name,
                "repo_url": self.repo.html_url
            })

            return {
                "repo_name": self.repo.full_name,
                "repo_url": self.repo.html_url,
                "default_branch": self.repo.default_branch,
                "is_private": self.repo.private,
                "description": self.repo.description
            }

        except Exception as e:
            self.log_activity("set_repository_error", {"repo_url": repo_url, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to connect to repository: {str(e)}")

    async def create_issue(self, title: str, body: str, labels: List[str] = None,
                          assignees: List[str] = None, milestone: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a GitHub issue for task tracking.

        Args:
            title: Issue title
            body: Issue description
            labels: List of label names
            assignees: List of GitHub usernames to assign
            milestone: Milestone title or number

        Returns:
            Created issue details
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )

            # Set milestone if provided
            if milestone:
                try:
                    # Try to find milestone by title
                    milestones = list(self.repo.get_milestones())
                    milestone_obj = None

                    for m in milestones:
                        if m.title == milestone:
                            milestone_obj = m
                            break

                    if milestone_obj:
                        issue.edit(milestone=milestone_obj)
                except:
                    pass  # Milestone setting failed, but issue was created

            self.log_activity("issue_created", {
                "issue_number": issue.number,
                "title": title,
                "labels": labels or [],
                "assignees": assignees or []
            })

            return {
                "issue_number": issue.number,
                "title": title,
                "url": issue.html_url,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees]
            }

        except Exception as e:
            self.log_activity("create_issue_error", {"title": title, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to create issue: {str(e)}")

    async def list_issues(self, state: str = "open", labels: List[str] = None,
                         assignee: Optional[str] = None, max_issues: int = 20) -> Dict[str, Any]:
        """
        List repository issues with filtering.

        Args:
            state: Issue state (open, closed, all)
            labels: Filter by labels
            assignee: Filter by assignee
            max_issues: Maximum issues to return

        Returns:
            List of issues with details
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Get issues with filters
            issues = self.repo.get_issues(
                state=state,
                labels=labels or [],
                assignee=assignee,
                sort="updated",
                direction="desc"
            )

            issue_list = []
            for i, issue in enumerate(issues):
                if i >= max_issues:
                    break

                # Skip pull requests (GitHub API returns PRs as issues)
                if issue.pull_request:
                    continue

                issue_list.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "url": issue.html_url,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "milestone": issue.milestone.title if issue.milestone else None,
                    "comments": issue.comments
                })

            return {
                "issues": issue_list,
                "total_returned": len(issue_list),
                "state_filter": state,
                "labels_filter": labels,
                "assignee_filter": assignee
            }

        except Exception as e:
            self.log_activity("list_issues_error", {"state": state, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to list issues: {str(e)}")

    async def update_issue(self, issue_number: int, title: Optional[str] = None,
                          body: Optional[str] = None, state: Optional[str] = None,
                          labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update an existing GitHub issue.

        Args:
            issue_number: Issue number to update
            title: New title (optional)
            body: New body (optional)
            state: New state (open/closed)
            labels: New labels list (optional)

        Returns:
            Updated issue details
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Get the issue
            issue = self.repo.get_issue(issue_number)

            # Update issue with provided parameters
            update_params = {}
            if title is not None:
                update_params["title"] = title
            if body is not None:
                update_params["body"] = body
            if state is not None:
                update_params["state"] = state
            if labels is not None:
                update_params["labels"] = labels

            if update_params:
                issue.edit(**update_params)

            self.log_activity("issue_updated", {
                "issue_number": issue_number,
                "updates": list(update_params.keys())
            })

            return {
                "issue_number": issue_number,
                "title": issue.title,
                "state": issue.state,
                "url": issue.html_url,
                "updated_fields": list(update_params.keys())
            }

        except Exception as e:
            self.log_activity("update_issue_error", {"issue_number": issue_number, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to update issue: {str(e)}")

    async def create_milestone(self, title: str, description: str,
                              due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a project milestone.

        Args:
            title: Milestone title
            description: Milestone description
            due_date: Due date in ISO format (YYYY-MM-DD)

        Returns:
            Created milestone details
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Create milestone
            from datetime import datetime
            due_on = None
            if due_date:
                try:
                    due_on = datetime.fromisoformat(due_date)
                except:
                    pass

            milestone = self.repo.create_milestone(
                title=title,
                description=description,
                due_on=due_on
            )

            self.log_activity("milestone_created", {
                "title": title,
                "due_date": due_date
            })

            return {
                "number": milestone.number,
                "title": title,
                "description": description,
                "url": milestone.html_url,
                "state": milestone.state,
                "due_on": milestone.due_on.isoformat() if milestone.due_on else None
            }

        except Exception as e:
            self.log_activity("create_milestone_error", {"title": title, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to create milestone: {str(e)}")

    async def list_milestones(self, state: str = "open") -> Dict[str, Any]:
        """
        List repository milestones.

        Args:
            state: Milestone state (open, closed, all)

        Returns:
            List of milestones
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            milestones = list(self.repo.get_milestones(state=state))

            milestone_list = []
            for milestone in milestones:
                milestone_list.append({
                    "number": milestone.number,
                    "title": milestone.title,
                    "description": milestone.description,
                    "state": milestone.state,
                    "url": milestone.html_url,
                    "due_on": milestone.due_on.isoformat() if milestone.due_on else None,
                    "open_issues": milestone.open_issues,
                    "closed_issues": milestone.closed_issues
                })

            return {
                "milestones": milestone_list,
                "total_count": len(milestone_list),
                "state_filter": state
            }

        except Exception as e:
            self.log_activity("list_milestones_error", {"state": state, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to list milestones: {str(e)}")

    async def update_repository_settings(self, description: Optional[str] = None,
                                        topics: Optional[List[str]] = None,
                                        private: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update repository settings.

        Args:
            description: New repository description
            topics: Repository topics/tags
            private: Whether repository should be private

        Returns:
            Updated repository settings
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            updates = {}
            if description is not None:
                updates["description"] = description
            if private is not None:
                updates["private"] = private

            if updates:
                self.repo.edit(**updates)

            # Update topics separately (different API)
            if topics is not None:
                self.repo.replace_topics(topics)

            self.log_activity("repository_settings_updated", {
                "updates": list(updates.keys()),
                "topics_updated": topics is not None
            })

            return {
                "repo_name": self.repo.full_name,
                "description": self.repo.description,
                "private": self.repo.private,
                "topics": self.repo.get_topics(),
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            self.log_activity("update_repo_settings_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to update repository settings: {str(e)}")

    async def add_repository_topics(self, topics: List[str]) -> Dict[str, Any]:
        """
        Add topics to repository.

        Args:
            topics: List of topic strings

        Returns:
            Updated topics list
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Get current topics and add new ones
            current_topics = self.repo.get_topics()
            all_topics = list(set(current_topics + topics))

            # Update topics
            self.repo.replace_topics(all_topics)

            self.log_activity("topics_added", {
                "new_topics": topics,
                "total_topics": len(all_topics)
            })

            return {
                "topics": all_topics,
                "added_topics": topics,
                "total_topics": len(all_topics)
            }

        except Exception as e:
            self.log_activity("add_topics_error", {"topics": topics, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to add repository topics: {str(e)}")

    async def get_repository_insights(self) -> Dict[str, Any]:
        """
        Get repository insights and analytics.

        Returns:
            Repository analytics and insights
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Get basic repository stats
            insights = {
                "repo_name": self.repo.full_name,
                "description": self.repo.description,
                "stars": self.repo.stargazers_count,
                "forks": self.repo.forks_count,
                "watchers": self.repo.watchers_count,
                "open_issues": self.repo.open_issues_count,
                "language": self.repo.language,
                "size_kb": self.repo.size,
                "created_at": self.repo.created_at.isoformat(),
                "updated_at": self.repo.updated_at.isoformat(),
                "default_branch": self.repo.default_branch
            }

            # Get recent activity
            try:
                commits = list(self.repo.get_commits()[:10])  # Last 10 commits
                insights["recent_commits"] = len(commits)
                if commits:
                    insights["last_commit"] = {
                        "sha": commits[0].sha[:8],
                        "message": commits[0].commit.message.split('\n')[0],
                        "author": commits[0].commit.author.name,
                        "date": commits[0].commit.author.date.isoformat()
                    }
            except:
                insights["recent_commits"] = 0

            # Get issue statistics
            try:
                open_issues = list(self.repo.get_issues(state="open"))
                closed_issues = list(self.repo.get_issues(state="closed")[:10])  # Sample
                insights["issue_stats"] = {
                    "open_count": len(open_issues),
                    "closed_sample": len(closed_issues)
                }
            except:
                insights["issue_stats"] = {"open_count": 0, "closed_sample": 0}

            # Get languages
            try:
                languages = self.repo.get_languages()
                insights["languages"] = dict(languages)
            except:
                insights["languages"] = {}

            return insights

        except Exception as e:
            self.log_activity("get_insights_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get repository insights: {str(e)}")

    async def setup_issue_templates(self) -> Dict[str, Any]:
        """
        Set up issue templates for better project organization.

        Returns:
            Template setup result
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            # Feature request template
            feature_template = """---
name: Feature Request
about: Suggest a new feature for the project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
Describe your proposed solution.

## Alternatives Considered
Any alternative solutions you've considered.

## Additional Context
Any other context, screenshots, or examples.
"""

            # Bug report template
            bug_template = """---
name: Bug Report
about: Report a bug to help improve the project
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. iOS]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

## Additional Context
Screenshots, logs, or other context.
"""

            # Create templates
            templates_created = []

            try:
                self.repo.create_file(
                    path=".github/ISSUE_TEMPLATE/feature_request.md",
                    message="Add feature request template",
                    content=feature_template
                )
                templates_created.append("feature_request.md")
            except:
                pass

            try:
                self.repo.create_file(
                    path=".github/ISSUE_TEMPLATE/bug_report.md",
                    message="Add bug report template",
                    content=bug_template
                )
                templates_created.append("bug_report.md")
            except:
                pass

            self.log_activity("issue_templates_setup", {
                "templates_created": templates_created
            })

            return {
                "templates_created": templates_created,
                "total_templates": len(templates_created),
                "status": "completed" if templates_created else "failed"
            }

        except Exception as e:
            self.log_activity("setup_templates_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to setup issue templates: {str(e)}")

    async def create_pull_request(self, title: str, body: str, head_branch: str,
                                 base_branch: str = "main") -> Dict[str, Any]:
        """
        Create a pull request.

        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch

        Returns:
            Created PR details
        """
        try:
            if not self.repo:
                raise MCPToolError("Repository not set. Call set_repository first.")

            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )

            self.log_activity("pull_request_created", {
                "pr_number": pr.number,
                "title": title,
                "head_branch": head_branch,
                "base_branch": base_branch
            })

            return {
                "pr_number": pr.number,
                "title": title,
                "url": pr.html_url,
                "state": pr.state,
                "head_branch": head_branch,
                "base_branch": base_branch,
                "created_at": pr.created_at.isoformat()
            }

        except Exception as e:
            self.log_activity("create_pr_error", {"title": title, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to create pull request: {str(e)}")