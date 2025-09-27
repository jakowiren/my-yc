"""
CEO Service - Stable Modal web service for CEO agents
Provides stable endpoints that won't change between deployments
"""

import modal
from typing import Dict, Any

# STABLE app name - this ensures consistent URLs
app = modal.App("my-yc-ceo")

# Persistent volume for all startup workspaces
startup_workspaces = modal.Volume.from_name("startup-workspaces", create_if_missing=True)

# Container image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai>=1.0.0",
    "PyGithub>=1.59.0",
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
    "gitpython>=3.1.0"
).add_local_file(
    local_path="ceo_agent.py",
    remote_path="/root/ceo_agent.py"
).add_local_file(
    local_path="workspace_manager.py",
    remote_path="/root/workspace_manager.py"
).add_local_dir(
    local_path="mcp_tools",
    remote_path="/root/mcp_tools"
)

# Request/Response models will be defined inside functions to avoid import issues

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=300,
    cpu=2,
    memory=4096,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="POST", label="initialize")
async def initialize_ceo(request_data: Dict[str, Any]):
    """
    Initialize CEO agent for a startup.
    Stable endpoint: https://jakowiren--my-yc-ceo-initialize.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from ceo_agent import CEOAgent
        from workspace_manager import WorkspaceManager

        startup_id = request_data.get("startup_id")
        design_doc = request_data.get("design_doc")

        if not startup_id or not design_doc:
            return {
                "success": False,
                "error": "startup_id and design_doc are required"
            }

        print(f"🤖 Initializing CEO for startup: {startup_id}")
        startup_name = design_doc.get("title", f"Startup {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace already exists
        if workspace_mgr.workspace_exists(startup_id):
            print(f"📁 Workspace already exists for {startup_id}")
            # Load existing CEO
            ceo = CEOAgent(startup_id, design_doc, workspace_mgr)
            result = {
                "success": True,
                "startup_id": startup_id,
                "status": "resumed",
                "message": f"CEO workspace resumed for '{startup_name}'",
                "workspace_info": workspace_mgr.get_workspace_info(startup_id)
            }
        else:
            print(f"🏗️ Creating new workspace for {startup_id}")
            # Initialize workspace
            workspace_path = workspace_mgr.initialize_workspace(startup_id, startup_name, design_doc)

            # Create CEO instance with workspace
            ceo = CEOAgent(startup_id, design_doc, workspace_mgr)

            # Initialize the project (creates GitHub repo)
            result = await ceo.initialize_project()

        # Update workspace activity
        workspace_mgr.update_last_activity(startup_id)

        print(f"🎉 CEO initialization result: {result}")
        return result

    except Exception as e:
        print(f"❌ CEO initialization failed: {str(e)}")
        return {
            "success": False,
            "error": f"CEO initialization failed: {str(e)}",
            "startup_id": request_data.get("startup_id")
        }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=60,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="POST", label="chat")
async def chat_with_ceo(request_data: Dict[str, Any]):
    """
    Chat with CEO agent.
    Stable endpoint: https://jakowiren--my-yc-ceo-chat.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from ceo_agent import CEOAgent
        from workspace_manager import WorkspaceManager

        startup_id = request_data.get("startup_id")
        message = request_data.get("message")

        if not startup_id or not message:
            return {
                "success": False,
                "error": "startup_id and message are required"
            }

        print(f"💬 Chat request for startup: {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace exists
        if not workspace_mgr.workspace_exists(startup_id):
            return {
                "success": False,
                "error": "CEO not initialized for this startup. Please initialize first."
            }

        # Load CEO from workspace (this will load all persistent state)
        print(f"📁 Loading CEO from workspace: {startup_id}")

        # We need design_doc to create CEO instance, but we can load it from workspace
        workspace_info = workspace_mgr.get_workspace_info(startup_id)
        design_doc = workspace_info["metadata"]["design_document"]

        ceo = CEOAgent(startup_id, design_doc, workspace_mgr)

        # Use the new MCP-powered work request handler
        response = await ceo.handle_work_request(message)

        # Update workspace activity
        workspace_mgr.update_last_activity(startup_id)

        return {
            "success": True,
            "response": response,
            "startup_id": startup_id,
            "workspace_info": {
                "last_activity": workspace_info["last_activity"],
                "conversation_count": workspace_info["conversation_count"] + 1
            }
        }

    except Exception as e:
        print(f"❌ Chat failed: {str(e)}")
        return {
            "success": False,
            "error": f"Chat failed: {str(e)}"
        }

@app.function(
    image=image,
    timeout=30,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="GET", label="status")
async def get_ceo_status(startup_id: str):
    """
    Get CEO status.
    Stable endpoint: https://jakowiren--my-yc-ceo-status.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from workspace_manager import WorkspaceManager

        print(f"📊 Status request for startup: {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace exists
        if not workspace_mgr.workspace_exists(startup_id):
            return {
                "startup_id": startup_id,
                "ceo_status": "not_initialized",
                "message": "CEO not found. Please initialize first."
            }

        # Get workspace info
        workspace_info = workspace_mgr.get_workspace_info(startup_id)

        return {
            "startup_id": startup_id,
            "ceo_status": workspace_info["ceo_status"],
            "workspace_path": workspace_info["workspace_path"],
            "last_activity": workspace_info["last_activity"],
            "conversation_count": workspace_info["conversation_count"],
            "team_plan_exists": workspace_info["team_plan_exists"],
            "metadata": workspace_info["metadata"]
        }

    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        return {
            "startup_id": startup_id,
            "ceo_status": "error",
            "error": str(e)
        }

@app.function(image=image, timeout=30, volumes={"/workspace": startup_workspaces})
@modal.fastapi_endpoint(method="GET", label="health")
async def health_check():
    """
    Health check endpoint.
    Stable endpoint: https://jakowiren--my-yc-ceo-health.modal.run
    """
    import os
    workspace_count = 0
    try:
        if os.path.exists("/workspace"):
            workspace_count = len([d for d in os.listdir("/workspace") if os.path.isdir(os.path.join("/workspace", d))])
    except Exception:
        workspace_count = 0

    return {
        "status": "healthy",
        "service": "my-yc-ceo",
        "active_workspaces": workspace_count
    }

if __name__ == "__main__":
    print("🚀 CEO Service ready for deployment")
    print("Stable endpoints will be:")
    print("  Initialize: https://jakowiren--my-yc-ceo-initialize.modal.run")
    print("  Chat:       https://jakowiren--my-yc-ceo-chat.modal.run")
    print("  Status:     https://jakowiren--my-yc-ceo-status.modal.run")
    print("  Health:     https://jakowiren--my-yc-ceo-health.modal.run")
    print("Deploy with: modal deploy ceo_service.py")