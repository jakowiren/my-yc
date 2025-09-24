"""
MCP Server for GitHub Operations
Handles autonomous GitHub repository creation, management, and deployments.
"""

import os
import asyncio
from typing import Dict, Any, List
from github import Github
from mcp import Server, Tool, types
from pydantic import BaseModel
import json

# Initialize GitHub client
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")

github_client = Github(GITHUB_TOKEN)

# MCP Server setup
server = Server("github-operations")

class CreateRepoRequest(BaseModel):
    name: str
    description: str
    private: bool = True
    auto_init: bool = True
    gitignore_template: str = "Python"

class CreateFileRequest(BaseModel):
    repo_name: str
    file_path: str
    content: str
    commit_message: str

@server.tool()
async def create_repository(request: CreateRepoRequest) -> Dict[str, Any]:
    """
    Create a new GitHub repository for the project.

    Args:
        request: Repository creation parameters

    Returns:
        Dictionary with repository details
    """
    try:
        user = github_client.get_user()

        # Create repository
        repo = user.create_repo(
            name=request.name,
            description=request.description,
            private=request.private,
            auto_init=request.auto_init,
            gitignore_template=request.gitignore_template
        )

        return {
            "success": True,
            "repo_name": repo.name,
            "repo_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "default_branch": repo.default_branch,
            "message": f"Repository '{request.name}' created successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create repository '{request.name}'"
        }

@server.tool()
async def create_file(request: CreateFileRequest) -> Dict[str, Any]:
    """
    Create or update a file in the repository.

    Args:
        request: File creation parameters

    Returns:
        Dictionary with operation status
    """
    try:
        user = github_client.get_user()
        repo = user.get_repo(request.repo_name)

        # Create or update file
        try:
            # Try to get existing file first
            existing_file = repo.get_contents(request.file_path)
            repo.update_file(
                request.file_path,
                request.commit_message,
                request.content,
                existing_file.sha
            )
            action = "updated"
        except:
            # File doesn't exist, create it
            repo.create_file(
                request.file_path,
                request.commit_message,
                request.content
            )
            action = "created"

        return {
            "success": True,
            "action": action,
            "file_path": request.file_path,
            "repo_name": request.repo_name,
            "message": f"File '{request.file_path}' {action} successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create file '{request.file_path}'"
        }

@server.tool()
async def setup_project_structure(repo_name: str, project_type: str = "nextjs") -> Dict[str, Any]:
    """
    Set up initial project structure in the repository.

    Args:
        repo_name: Name of the repository
        project_type: Type of project (nextjs, python, etc.)

    Returns:
        Dictionary with setup status
    """
    try:
        templates = {
            "nextjs": {
                "package.json": {
                    "name": repo_name.lower(),
                    "version": "0.1.0",
                    "private": True,
                    "scripts": {
                        "dev": "next dev",
                        "build": "next build",
                        "start": "next start"
                    },
                    "dependencies": {
                        "next": "^14.0.0",
                        "react": "^18.0.0",
                        "react-dom": "^18.0.0"
                    }
                },
                "README.md": f"# {repo_name}\n\nAutonomously generated project by my-yc.\n\n## Getting Started\n\n```bash\nnpm install\nnpm run dev\n```",
                "next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {}\n\nmodule.exports = nextConfig",
                ".env.example": "# Environment variables\nNEXT_PUBLIC_APP_NAME=" + repo_name
            }
        }

        if project_type not in templates:
            return {
                "success": False,
                "error": f"Unsupported project type: {project_type}",
                "message": f"Project type '{project_type}' is not supported"
            }

        template = templates[project_type]
        user = github_client.get_user()
        repo = user.get_repo(repo_name)

        created_files = []

        for file_path, content in template.items():
            if isinstance(content, dict):
                # JSON files
                file_content = json.dumps(content, indent=2)
            else:
                file_content = content

            try:
                repo.create_file(
                    file_path,
                    f"Initialize {file_path}",
                    file_content
                )
                created_files.append(file_path)
            except Exception as file_error:
                print(f"Warning: Could not create {file_path}: {file_error}")

        return {
            "success": True,
            "created_files": created_files,
            "project_type": project_type,
            "repo_name": repo_name,
            "message": f"Project structure set up for {project_type} project"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to set up project structure for '{repo_name}'"
        }

@server.tool()
async def get_repository_info(repo_name: str) -> Dict[str, Any]:
    """
    Get information about a repository.

    Args:
        repo_name: Name of the repository

    Returns:
        Dictionary with repository information
    """
    try:
        user = github_client.get_user()
        repo = user.get_repo(repo_name)

        return {
            "success": True,
            "name": repo.name,
            "description": repo.description,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "default_branch": repo.default_branch,
            "private": repo.private,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "size": repo.size
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get repository info for '{repo_name}'"
        }

async def main():
    """Run the MCP server."""
    print("🐙 Starting GitHub MCP Server...")
    print(f"📡 Server listening on port 8001")

    # Run the server
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())