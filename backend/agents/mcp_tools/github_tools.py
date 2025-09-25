"""
Embedded GitHub MCP Tools for Modal Agents
Direct GitHub API integration without server overhead.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from github import Github
from pathlib import Path


class GitHubMCPTools:
    """Embedded GitHub tools for autonomous agents."""

    def __init__(self, github_token: Optional[str] = None):
        """Initialize GitHub MCP tools with authentication."""
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")

        self.client = Github(self.github_token)
        self.user = self.client.get_user()

    async def create_repository(
        self,
        name: str,
        description: str,
        private: bool = False,
        auto_init: bool = True,
        gitignore_template: str = "Node"
    ) -> Dict[str, Any]:
        """
        Create a new GitHub repository.

        Args:
            name: Repository name (will be made unique if needed)
            description: Repository description
            private: Whether the repository should be private
            auto_init: Whether to initialize with README
            gitignore_template: Template for .gitignore file

        Returns:
            Dictionary with repository details and status
        """
        try:
            # Ensure unique repository name
            original_name = name
            counter = 1

            while True:
                try:
                    # Check if repo already exists
                    existing = self.user.get_repo(name)
                    # If we get here, repo exists, try a new name
                    name = f"{original_name}-{counter}"
                    counter += 1
                except:
                    # Repo doesn't exist, we can use this name
                    break

            # Create the repository
            repo = self.user.create_repo(
                name=name,
                description=f"🤖 {description} | Autonomous startup created by my-yc AI agents",
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template
            )

            return {
                "success": True,
                "repo_name": repo.name,
                "repo_url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "default_branch": repo.default_branch,
                "message": f"Repository '{name}' created successfully",
                "data": {
                    "full_name": repo.full_name,
                    "created_at": repo.created_at.isoformat(),
                    "owner": repo.owner.login
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create repository '{name}': {str(e)}"
            }

    async def create_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create or update a file in the repository.

        Args:
            repo_name: Name of the repository
            file_path: Path to the file within the repo
            content: File content
            commit_message: Commit message
            branch: Target branch

        Returns:
            Dictionary with operation status
        """
        try:
            repo = self.user.get_repo(repo_name)

            try:
                # Try to get existing file
                existing_file = repo.get_contents(file_path, ref=branch)
                # File exists, update it
                repo.update_file(
                    file_path,
                    commit_message,
                    content,
                    existing_file.sha,
                    branch=branch
                )
                action = "updated"
            except:
                # File doesn't exist, create it
                repo.create_file(
                    file_path,
                    commit_message,
                    content,
                    branch=branch
                )
                action = "created"

            return {
                "success": True,
                "action": action,
                "file_path": file_path,
                "repo_name": repo_name,
                "message": f"File '{file_path}' {action} successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to {action if 'action' in locals() else 'modify'} file '{file_path}': {str(e)}"
            }

    async def setup_nextjs_project(
        self,
        repo_name: str,
        project_title: str,
        project_description: str
    ) -> Dict[str, Any]:
        """
        Set up a complete Next.js project structure in the repository.

        Args:
            repo_name: Name of the repository
            project_title: Human-readable project title
            project_description: Project description

        Returns:
            Dictionary with setup status and created files
        """
        try:
            repo = self.user.get_repo(repo_name)
            created_files = []

            # Project templates
            templates = {
                "package.json": {
                    "name": repo_name.lower().replace(" ", "-"),
                    "version": "0.1.0",
                    "private": True,
                    "description": project_description,
                    "scripts": {
                        "dev": "next dev",
                        "build": "next build",
                        "start": "next start",
                        "lint": "next lint"
                    },
                    "dependencies": {
                        "next": "^14.2.0",
                        "react": "^18.3.0",
                        "react-dom": "^18.3.0"
                    },
                    "devDependencies": {
                        "@types/node": "^20.14.0",
                        "@types/react": "^18.3.0",
                        "@types/react-dom": "^18.3.0",
                        "typescript": "^5.5.0",
                        "eslint": "^8.57.0",
                        "eslint-config-next": "^14.2.0"
                    }
                },

                "next.config.js": '''/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig''',

                "tsconfig.json": {
                    "compilerOptions": {
                        "target": "es5",
                        "lib": ["dom", "dom.iterable", "es6"],
                        "allowJs": True,
                        "skipLibCheck": True,
                        "strict": True,
                        "noEmit": True,
                        "esModuleInterop": True,
                        "module": "esnext",
                        "moduleResolution": "bundler",
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "jsx": "preserve",
                        "incremental": True,
                        "plugins": [{"name": "next"}],
                        "baseUrl": ".",
                        "paths": {"@/*": ["./*"]}
                    },
                    "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                    "exclude": ["node_modules"]
                },

                "app/layout.tsx": f'''import type {{ Metadata }} from 'next'
import {{ Inter }} from 'next/font/google'
import './globals.css'

const inter = Inter({{ subsets: ['latin'] }})

export const metadata: Metadata = {{
  title: '{project_title}',
  description: '{project_description}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body className={{inter.className}}>{{children}}</body>
    </html>
  )
}}''',

                "app/page.tsx": f'''export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          {project_title}
        </h1>
        <p className="text-center text-gray-600 mb-8">
          {project_description}
        </p>
        <div className="text-center">
          <p className="text-sm text-gray-400">
            🤖 Autonomously created by my-yc AI agents
          </p>
        </div>
      </div>
    </main>
  )
}}''',

                "app/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 0, 0, 0;
    --background-end-rgb: 0, 0, 0;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}''',

                ".env.example": f'''# {project_title} Environment Variables
NEXT_PUBLIC_APP_NAME="{project_title}"
# Add your environment variables here''',

                "README.md": f'''# {project_title}

> 🤖 **Autonomous Startup** | Created by AI agents via [my-yc](https://my-yc.com) platform

{project_description}

## 🚀 Quick Start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your autonomous startup!

## 🤖 Autonomous Generation

This project was created by AI agents that:

- ✅ Analyzed your startup idea
- ✅ Generated complete project structure
- ✅ Set up development environment
- ✅ Created responsive UI components
- ✅ Configured for immediate deployment

## 🔄 Next Steps

Deploy and scale autonomously:

- **Deploy**: Ready for Vercel deployment
- **Develop**: Add features and functionality
- **Scale**: Self-contained and independent
- **Integrate**: Database, auth, payments ready

---

*🤖 Autonomously generated by [my-yc](https://my-yc.com) AI agents*
'''
            }

            # Create all files
            for file_path, content in templates.items():
                if isinstance(content, dict):
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
                "repo_name": repo_name,
                "project_type": "nextjs",
                "message": f"Next.js project '{project_title}' set up successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to set up Next.js project: {str(e)}"
            }

    async def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a repository.

        Args:
            repo_name: Name of the repository

        Returns:
            Dictionary with repository information
        """
        try:
            repo = self.user.get_repo(repo_name)

            return {
                "success": True,
                "name": repo.name,
                "full_name": repo.full_name,
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
                "size": repo.size,
                "owner": repo.owner.login
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get repository info for '{repo_name}'"
            }