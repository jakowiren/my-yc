"""
Simple MVP Agent for my-yc
Creates GitHub repository and writes design document to README.
"""

import modal
import json
import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

# Modal app definition
app = modal.App("my-yc-mvp")

# Container image with minimal dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "PyGithub>=1.59.0",       # GitHub API client
    "requests>=2.31.0",       # HTTP client
    "fastapi>=0.100.0",       # For web endpoints
)

@app.function(
    image=image,
    cpu=1,
    memory=1024,
    timeout=300,  # 5 minutes max runtime
    secrets=[modal.Secret.from_name("my-yc-secrets")],  # GitHub token and other credentials
)
def create_startup_repo(project_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a GitHub repository with design document as README.

    Args:
        project_id: Unique identifier for the project
        config: Configuration including design_doc, title, etc.

    Returns:
        Dictionary with creation results including repo URL
    """
    print(f"🚀 Creating startup repo for project: {project_id}")

    try:
        # Extract configuration
        design_doc = config.get("design_doc", {})
        title = design_doc.get("title", config.get("title", "My Startup"))
        user_id = config.get("user_id", "unknown")

        print(f"📋 Title: {title}")
        print(f"👤 User: {user_id}")

        # Get GitHub token from environment
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise Exception("GITHUB_TOKEN not found in environment")

        print("🔑 GitHub token found")

        # Import PyGithub
        from github import Github

        # Initialize GitHub client
        g = Github(github_token)
        user = g.get_user()

        print(f"✅ Authenticated as GitHub user: {user.login}")

        # Generate repository name
        # Clean title and add project prefix
        repo_name = title.lower().replace(" ", "-").replace("_", "-")
        repo_name = "".join(c for c in repo_name if c.isalnum() or c in "-")
        repo_name = f"startup-{repo_name}-{project_id[:8]}"

        print(f"📦 Creating repository: {repo_name}")

        # Create repository
        repo = user.create_repo(
            name=repo_name,
            description=design_doc.get("executive_summary", "A startup created by my-yc AI agents"),
            private=False,  # Public for demo purposes
            auto_init=True,
            gitignore_template="Node"
        )

        print(f"✅ Repository created: {repo.html_url}")

        # Generate README content from design document
        readme_content = generate_readme_from_design_doc(design_doc, repo.html_url)

        # Update README.md
        try:
            # Get existing README
            readme_file = repo.get_contents("README.md")
            repo.update_file(
                path="README.md",
                message="Update README with startup design document",
                content=readme_content,
                sha=readme_file.sha
            )
        except:
            # Create new README if it doesn't exist
            repo.create_file(
                path="README.md",
                message="Add startup design document",
                content=readme_content
            )

        print("📄 README.md updated with design document")

        # Create basic project structure
        create_basic_project_structure(repo, design_doc)

        return {
            "success": True,
            "project_id": project_id,
            "repo_url": repo.html_url,
            "repo_name": repo_name,
            "clone_url": repo.clone_url,
            "message": f"Successfully created startup repository: {repo_name}"
        }

    except Exception as e:
        print(f"❌ Error creating startup repo: {str(e)}")
        return {
            "success": False,
            "project_id": project_id,
            "error": str(e),
            "message": f"Failed to create repository: {str(e)}"
        }

def generate_readme_from_design_doc(design_doc: Dict[str, Any], repo_url: str) -> str:
    """Generate README.md content from design document."""

    title = design_doc.get("title", "My Startup")
    exec_summary = design_doc.get("executive_summary", "A startup created by AI agents")
    problem = design_doc.get("problem_statement", "")
    target_market = design_doc.get("target_market", "")
    user_persona = design_doc.get("user_persona", "")
    value_prop = design_doc.get("value_proposition", "")
    mvp_features = design_doc.get("mvp_features", [])
    tech_requirements = design_doc.get("technical_requirements", "")
    tech_stack = design_doc.get("tech_stack", [])
    success_metrics = design_doc.get("success_metrics", [])
    next_steps = design_doc.get("immediate_next_steps", [])
    category = design_doc.get("category", "web-app")
    complexity = design_doc.get("complexity_level", "moderate")
    dev_time = design_doc.get("estimated_dev_time", "2-4 weeks")

    readme = f"""# {title}

> 🤖 **AI-Generated Startup** | Created by autonomous agents via [my-yc](https://my-yc.com)

{exec_summary}

## 🚀 Quick Start

This repository contains the complete startup specification and will be developed into a full application by AI agents.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url={repo_url})

## 📋 Startup Overview

- **Category**: {category.replace("-", " ").title()}
- **Complexity**: {complexity.title()}
- **Estimated Development Time**: {dev_time}
- **Created**: {datetime.now().strftime('%Y-%m-%d')}

## 🎯 Problem Statement

{problem}

## 👥 Target Market

**Market**: {target_market}

**User Persona**: {user_persona}

## 💡 Value Proposition

{value_prop}

## 🚀 MVP Features

{chr(10).join(f"- {feature}" for feature in mvp_features)}

## 🛠️ Technical Approach

{tech_requirements}

### Technology Stack

{chr(10).join(f"- {tech}" for tech in tech_stack)}

## 📊 Success Metrics

{chr(10).join(f"- {metric}" for metric in success_metrics)}

## 🎯 Implementation Roadmap

{chr(10).join(f"- [ ] {step}" for step in next_steps)}

## 🤖 AI Agent Development

This startup is being developed by autonomous AI agents that will:

1. **Set up the development environment**
2. **Create the application architecture**
3. **Implement core features**
4. **Add styling and UI/UX**
5. **Deploy to production**
6. **Monitor and iterate**

## 📁 Repository Structure

```
{title.lower().replace(" ", "-")}/
├── README.md          # This file - startup specification
├── docs/              # Additional documentation
├── src/               # Source code (will be generated)
├── tests/             # Test files (will be generated)
├── .env.example       # Environment variables template
└── package.json       # Project dependencies (will be generated)
```

## 🔧 Development Status

- [x] Design document created
- [x] Repository initialized
- [ ] Development environment setup
- [ ] Core features implementation
- [ ] UI/UX implementation
- [ ] Testing and deployment

## 📞 Contact & Support

This startup was automatically generated by the [my-yc](https://my-yc.com) platform.

For questions about this repository or the AI agent development process, please visit [my-yc.com](https://my-yc.com).

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC by AI agents*
"""

    return readme

def create_basic_project_structure(repo, design_doc: Dict[str, Any]):
    """Create basic project structure files."""

    try:
        # Create .env.example
        env_example = """# Environment Variables Template
# Copy this file to .env and fill in your values

# Database
DATABASE_URL=your_database_url_here

# API Keys
API_KEY=your_api_key_here

# App Configuration
APP_ENV=development
APP_PORT=3000
"""

        repo.create_file(
            path=".env.example",
            message="Add environment variables template",
            content=env_example
        )

        # Create docs directory with initial file
        docs_content = f"""# {design_doc.get('title', 'Startup')} Documentation

This directory will contain additional documentation for the startup as it's developed by AI agents.

## Planned Documentation

- [ ] API Documentation
- [ ] Deployment Guide
- [ ] User Manual
- [ ] Development Guide
- [ ] Architecture Overview

---

*This documentation will be automatically generated as the project develops.*
"""

        repo.create_file(
            path="docs/README.md",
            message="Initialize documentation directory",
            content=docs_content
        )

        print("📁 Basic project structure created")

    except Exception as e:
        print(f"⚠️ Warning: Could not create basic structure: {e}")

# Web endpoint for Supabase Edge Functions
@app.function(
    image=image,
    cpu=1,
    memory=512,
    timeout=60,
    secrets=[modal.Secret.from_name("my-yc-secrets")]
)
@modal.fastapi_endpoint(method="POST")
def spawn_project_web(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Web endpoint for spawning projects from Supabase Edge Functions.

    Expects JSON payload:
    {
        "project_id": "uuid-string",
        "config": {
            "title": "Project Title",
            "description": "Project description",
            "design_doc": {...},
            "user_id": "user-uuid"
        }
    }
    """
    try:
        project_id = request_data.get("project_id")
        config = request_data.get("config", {})

        if not project_id:
            return {"success": False, "error": "project_id is required"}

        if not config.get("design_doc"):
            return {"success": False, "error": "config.design_doc is required"}

        print(f"🌐 Web endpoint called for project: {project_id}")

        # Call the main function
        result = create_startup_repo.remote(project_id, config)

        return result

    except Exception as e:
        print(f"❌ Web endpoint error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to spawn project"
        }

if __name__ == "__main__":
    # Local testing
    import uuid

    test_project_id = str(uuid.uuid4())[:8]
    test_config = {
        "title": "AI Recipe Recommender",
        "design_doc": {
            "title": "AI Recipe Recommender",
            "executive_summary": "An AI-powered app that recommends personalized recipes based on dietary preferences and available ingredients.",
            "problem_statement": "People struggle to find recipes that match their dietary needs and available ingredients.",
            "target_market": "Health-conscious home cooks aged 25-45",
            "user_persona": "Busy professionals who want to eat healthy but have limited time for meal planning",
            "value_proposition": "Personalized recipe recommendations that save time and reduce food waste",
            "mvp_features": [
                "Recipe recommendation engine",
                "Dietary preference settings",
                "Ingredient-based search",
                "Shopping list generation"
            ],
            "technical_requirements": "Web app with AI recommendation engine and user preference storage",
            "tech_stack": [
                "Frontend: Next.js + TypeScript",
                "Backend: Node.js + Express",
                "Database: PostgreSQL",
                "AI: OpenAI API for recommendations"
            ],
            "success_metrics": [
                "User engagement rate",
                "Recipe completion rate",
                "User satisfaction scores"
            ],
            "immediate_next_steps": [
                "Set up development environment",
                "Create recipe database",
                "Implement recommendation algorithm",
                "Build user interface"
            ],
            "category": "food-tech",
            "complexity_level": "moderate",
            "estimated_dev_time": "3-4 weeks"
        },
        "user_id": "test-user-123"
    }

    print("Testing Modal agent locally...")
    with app.run():
        result = create_startup_repo.remote(test_project_id, test_config)
        print(f"Result: {result}")