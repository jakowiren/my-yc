"""
Modal.com project spawner for my-yc
Handles spawning isolated project instances in Modal containers.
"""

import modal
import asyncio
import json
from typing import Dict, Any
from pathlib import Path

# Modal app definition
app = modal.App("my-yc-spawner")

# Container image with agent dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "PyGithub>=1.59.0",       # GitHub API client
    "httpx>=0.25.0",          # HTTP client for Supabase integration
    "pydantic>=2.0.0",        # Data validation
    "python-dotenv>=1.0.0",   # Environment variables
    "openai>=1.0.0",          # Future: AI model integration
)

# Volume for persistent project state
project_volume = modal.Volume.from_name("my-yc-projects", create_if_missing=True)

@app.function(
    image=image,
    cpu=2,
    memory=4096,
    timeout=3600,  # 1 hour max runtime
    volumes={"/projects": project_volume},
    secrets=[modal.Secret.from_name("my-yc-secrets")],  # GitHub token and other credentials
    schedule=modal.Cron("0 */6 * * *")  # Wake every 6 hours
)
async def project_executor(project_id: str, project_config: Dict[str, Any]):
    """
    Execute an autonomous project in isolated Modal container.

    Args:
        project_id: Unique identifier for the project
        project_config: Configuration including idea, target market, etc.
    """
    print(f"🚀 Starting project execution for {project_id}")

    # Load project state
    project_state_path = Path(f"/projects/{project_id}/state.json")
    if project_state_path.exists():
        with open(project_state_path, 'r') as f:
            state = json.load(f)
        print(f"📂 Loaded existing project state")
    else:
        # Initialize new project
        state = {
            "project_id": project_id,
            "status": "initializing",
            "progress": 0,
            "agents": {},
            "services": {},
            "config": project_config
        }
        project_state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(project_state_path, 'w') as f:
            json.dump(state, f, indent=2)

    # Import and run agent orchestration
    try:
        from project_agents import run_agent_swarm

        # Execute the agent swarm
        result = await run_agent_swarm(project_id, state)

        # Update final state
        state.update(result)
        state["status"] = "sleeping"
        state["last_execution"] = str(asyncio.get_event_loop().time())

        with open(project_state_path, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"✅ Project {project_id} completed execution, going to sleep")

    except Exception as e:
        print(f"❌ Error in project {project_id}: {str(e)}")
        state["status"] = "error"
        state["error"] = str(e)

        with open(project_state_path, 'w') as f:
            json.dump(state, f, indent=2)

        raise

@app.function(
    image=image,
    cpu=1,
    memory=1024,
    timeout=60,
    secrets=[modal.Secret.from_name("my-yc-secrets")]
)
def spawn_project(project_id: str, idea_config: Dict[str, Any]) -> Dict[str, str]:
    """
    Spawn a new project instance.

    Args:
        project_id: Unique identifier for the project
        idea_config: Project idea and configuration

    Returns:
        Dictionary with spawn status and details
    """
    print(f"🌱 Spawning project {project_id}")

    # Schedule the project executor to run
    project_executor.spawn(project_id, idea_config)

    return {
        "project_id": project_id,
        "status": "spawned",
        "message": f"Project {project_id} spawned successfully in Modal container"
    }

@app.function(
    image=image,
    cpu=0.5,
    memory=512,
    timeout=30,
    volumes={"/projects": project_volume}
)
def get_project_status(project_id: str) -> Dict[str, Any]:
    """Get the current status of a project."""
    project_state_path = Path(f"/projects/{project_id}/state.json")

    if not project_state_path.exists():
        return {"error": "Project not found", "project_id": project_id}

    with open(project_state_path, 'r') as f:
        state = json.load(f)

    return state

@app.function(
    image=image,
    cpu=0.5,
    memory=512,
    timeout=30,
    volumes={"/projects": project_volume}
)
def list_projects() -> Dict[str, Any]:
    """List all active projects."""
    projects_dir = Path("/projects")
    projects = []

    if projects_dir.exists():
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                state_file = project_dir / "state.json"
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                    projects.append({
                        "project_id": state.get("project_id"),
                        "status": state.get("status"),
                        "progress": state.get("progress", 0),
                        "last_updated": state.get("last_execution")
                    })

    return {"projects": projects}

# Web endpoint for Supabase Edge Functions
@app.web_endpoint(method="POST", path="/spawn")
def spawn_project_web(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Web endpoint for spawning projects from Supabase Edge Functions.

    Expects JSON payload:
    {
        "project_id": "uuid-string",
        "config": {
            "title": "Project Title",
            "description": "Project description",
            "category": "optional-category"
        }
    }
    """
    try:
        project_id = request_data.get("project_id")
        config = request_data.get("config", {})

        if not project_id:
            return {"success": False, "error": "project_id is required"}

        if not config.get("title"):
            return {"success": False, "error": "config.title is required"}

        # Spawn the project asynchronously
        result = spawn_project.spawn(project_id, config)

        return {
            "success": True,
            "project_id": project_id,
            "message": "Project spawning initiated",
            "status": "spawning"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to spawn project"
        }

@app.web_endpoint(method="GET", path="/status/{project_id}")
def get_project_status_web(project_id: str) -> Dict[str, Any]:
    """Web endpoint to check project status."""
    try:
        result = get_project_status.remote(project_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get status for project {project_id}"
        }

if __name__ == "__main__":
    # Local testing
    import uuid

    test_project_id = str(uuid.uuid4())
    test_config = {
        "title": "AI Recipe Recommender",
        "description": "An AI-powered app that recommends recipes based on dietary preferences",
        "category": "food-tech",
        "target_market": "health-conscious consumers"
    }

    print("Testing Modal spawner locally...")
    with app.run():
        result = spawn_project.remote(test_project_id, test_config)
        print(f"Spawn result: {result}")

        # Check status
        import time
        time.sleep(5)
        status = get_project_status.remote(test_project_id)
        print(f"Project status: {status}")