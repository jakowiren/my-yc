"""
GitHub Agent for Autonomous Startup Creation
Creates and sets up GitHub repositories with complete project structure.
"""

import os
from typing import Dict, Any
from .base_agent import BaseAgent
from .mcp_tools.github_tools import GitHubMCPTools


class GitHubAgent(BaseAgent):
    """
    Agent responsible for GitHub repository creation and project setup.
    Uses embedded MCP tools for direct GitHub API integration.
    """

    def __init__(self, project_id: str, project_config: Dict[str, Any]):
        """Initialize GitHub agent with MCP tools."""
        super().__init__(project_id, project_config)

        # Initialize embedded MCP tools
        self.github_tools = GitHubMCPTools()

    async def execute(self) -> Dict[str, Any]:
        """
        Execute GitHub repository creation and project setup.

        Returns:
            Dictionary with execution results including repo details
        """
        try:
            await self.update_status("creating_repository", 10)

            # Extract project details
            project_title = self.project_config.get("title", "My Autonomous Startup")
            project_description = self.project_config.get("description", "An autonomous startup created by my-yc AI agents")
            category = self.project_config.get("category", "web-app")

            # Generate repository name
            repo_name = project_title.lower().replace(" ", "-").replace("_", "-")
            # Add project ID suffix to ensure uniqueness
            repo_name = f"{repo_name}-{self.project_id[:8]}"

            await self.log(f"Creating repository: {repo_name}")

            # Step 1: Create the repository
            repo_result = await self.github_tools.create_repository(
                name=repo_name,
                description=project_description,
                private=False,  # Public for demo purposes
                auto_init=True,
                gitignore_template="Node"
            )

            if not repo_result["success"]:
                return {
                    "success": False,
                    "error": repo_result["error"],
                    "message": f"Failed to create repository: {repo_result['error']}"
                }

            await self.log(f"Repository created successfully: {repo_result['repo_url']}")
            await self.update_status("setting_up_project", 50)

            # Step 2: Set up Next.js project structure
            await self.log("Setting up Next.js project structure")

            project_setup_result = await self.github_tools.setup_nextjs_project(
                repo_name=repo_result["repo_name"],
                project_title=project_title,
                project_description=project_description
            )

            if not project_setup_result["success"]:
                return {
                    "success": False,
                    "error": project_setup_result["error"],
                    "message": f"Failed to set up project structure: {project_setup_result['error']}"
                }

            await self.log(f"Project structure created: {len(project_setup_result['created_files'])} files")
            await self.update_status("finalizing", 90)

            # Step 3: Create enhanced README with deployment instructions
            await self.log("Creating deployment-ready README")

            enhanced_readme = f"""# {project_title}

> 🤖 **Autonomous Startup** | Created by AI agents via [my-yc](https://my-yc.com) platform

{project_description}

## 🚀 Live Demo

🌐 **Deploy instantly to Vercel:** [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url={repo_result['repo_url']})

## 📋 Project Details

- **Category**: {category.replace("-", " ").title()}
- **Created**: Autonomously by AI agents
- **Tech Stack**: Next.js 14, React 18, TypeScript
- **Status**: Ready for deployment

## 🛠️ Development

```bash
# Clone the repository
git clone {repo_result['clone_url']}
cd {repo_result['repo_name']}

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see your autonomous startup!

## 🚀 Deployment

### Vercel (Recommended)
1. Click the "Deploy with Vercel" button above
2. Connect your GitHub account
3. Your app will be live in minutes!

### Other Platforms
- **Netlify**: Connect your GitHub repo and deploy
- **Railway**: Deploy directly from GitHub
- **Custom**: Run `npm run build` and deploy the `out/` folder

## 🤖 Autonomous Features

This startup was created with the following autonomous capabilities:

- ✅ **Repository Creation**: GitHub repo with proper structure
- ✅ **Next.js Setup**: Complete TypeScript + React application
- ✅ **Component Architecture**: Scalable folder structure
- ✅ **Development Config**: ESLint, TypeScript, next.config.js
- ✅ **Production Ready**: Optimized build configuration
- ✅ **Deployment Ready**: One-click Vercel deployment

## 🔄 Next Steps

Your autonomous startup is ready to evolve:

1. **Customize Design**: Update components and styling
2. **Add Features**: Implement your core functionality
3. **Connect Database**: Add Supabase, Prisma, or your preferred DB
4. **User Authentication**: Implement auth with NextAuth.js
5. **Payment Processing**: Integrate Stripe for monetization
6. **Analytics**: Add tracking and user insights

## 🏗️ Architecture

```
{repo_result['repo_name']}/
├── app/                 # Next.js 14 app directory
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── globals.css     # Global styles
├── package.json        # Dependencies and scripts
├── next.config.js      # Next.js configuration
├── tsconfig.json       # TypeScript configuration
└── README.md          # This file
```

## 🤝 Contributing

This project was created autonomously but welcomes human contributions:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**🤖 Autonomously generated by [my-yc](https://my-yc.com) AI agents**

*Project ID: {self.project_id}*
*Created: {repo_result['data']['created_at']}*
*Repository: {repo_result['repo_url']}*
"""

            readme_result = await self.github_tools.create_file(
                repo_name=repo_result["repo_name"],
                file_path="README.md",
                content=enhanced_readme,
                commit_message="Enhanced README with deployment instructions and project details"
            )

            await self.update_status("completed", 100)

            # Return comprehensive result
            return {
                "success": True,
                "message": "GitHub repository and project setup completed successfully",
                "data": {
                    "repository": {
                        "name": repo_result["repo_name"],
                        "url": repo_result["repo_url"],
                        "clone_url": repo_result["clone_url"],
                        "ssh_url": repo_result["ssh_url"]
                    },
                    "project": {
                        "title": project_title,
                        "description": project_description,
                        "category": category,
                        "type": "nextjs",
                        "files_created": len(project_setup_result["created_files"]) + 1  # +1 for README
                    },
                    "deployment": {
                        "vercel_url": f"https://vercel.com/new/clone?repository-url={repo_result['repo_url']}",
                        "ready": True
                    }
                }
            }

        except Exception as e:
            await self.log(f"Execution error: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "message": f"GitHub agent execution failed: {str(e)}"
            }