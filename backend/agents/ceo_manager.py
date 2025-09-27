"""
CEO Manager - Routes requests to persistent CEO containers
Each startup gets its own dedicated CEO container that persists and sleeps between interactions.
"""

import modal
import json
from typing import Dict, Any, Optional
from datetime import datetime

app = modal.App("ceo-manager")

# Simple image for the manager
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "modal",
    "asyncio"
)

# Container registry: maps startup_id to container info
# In production, this would be backed by a persistent database
container_registry: Dict[str, Dict[str, Any]] = {}

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=300
)
@modal.fastapi_endpoint(method="POST", label="initialize")
async def initialize_ceo(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize a new CEO in a dedicated persistent container.
    Each startup gets its own container that will sleep between interactions.
    """
    try:
        startup_id = request_data.get("startup_id")
        design_doc = request_data.get("design_doc")

        if not startup_id or not design_doc:
            return {
                "success": False,
                "error": "startup_id and design_doc are required"
            }

        print(f"🚀 Creating persistent CEO container for startup: {startup_id}")

        # Create a dedicated CEO container for this startup
        container_app_name = f"ceo-{startup_id}"

        # Use Modal's container spawning to create persistent CEO
        # This will be a separate Modal app for this specific startup
        container_info = await _spawn_ceo_container(startup_id, design_doc, container_app_name)

        # Register the container
        container_registry[startup_id] = {
            "app_name": container_app_name,
            "container_url": container_info["container_url"],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        print(f"✅ CEO container created and registered for {startup_id}")

        return {
            "success": True,
            "startup_id": startup_id,
            "container_url": container_info["container_url"],
            "ceo_status": "initialized",
            **container_info.get("init_result", {})
        }

    except Exception as e:
        print(f"❌ Failed to initialize CEO container: {str(e)}")
        return {
            "success": False,
            "error": f"CEO container initialization failed: {str(e)}",
            "startup_id": request_data.get("startup_id")
        }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=60
)
@modal.fastapi_endpoint(method="POST", label="chat")
async def chat_with_ceo(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route chat message to the appropriate persistent CEO container.
    """
    try:
        startup_id = request_data.get("startup_id")
        message = request_data.get("message")

        if not startup_id or not message:
            return {
                "success": False,
                "error": "startup_id and message are required"
            }

        # Look up the CEO container for this startup
        container_info = container_registry.get(startup_id)
        if not container_info:
            return {
                "success": False,
                "error": f"No CEO container found for startup {startup_id}. Initialize first."
            }

        print(f"💬 Routing chat to CEO container for startup: {startup_id}")

        # Forward the message to the persistent CEO container
        chat_result = await _forward_to_ceo_container(container_info, message)

        return {
            "success": True,
            "startup_id": startup_id,
            "response": chat_result.get("response"),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Chat routing failed: {str(e)}")
        return {
            "success": False,
            "error": f"Chat failed: {str(e)}"
        }

@app.function(
    image=image,
    timeout=30
)
@modal.fastapi_endpoint(method="GET", label="status")
async def get_ceo_status(startup_id: str) -> Dict[str, Any]:
    """
    Get status of a CEO container.
    """
    try:
        container_info = container_registry.get(startup_id)
        if not container_info:
            return {
                "startup_id": startup_id,
                "ceo_status": "not_initialized",
                "message": "No CEO container found"
            }

        # Query the container status
        status = await _get_container_status(container_info)

        return {
            "startup_id": startup_id,
            "ceo_status": "active",
            "container_info": container_info,
            "detailed_status": status
        }

    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        return {
            "startup_id": startup_id,
            "ceo_status": "error",
            "error": str(e)
        }

@app.function(image=image, timeout=30)
@modal.fastapi_endpoint(method="GET", label="health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ceo-manager",
        "active_containers": len(container_registry),
        "registered_startups": list(container_registry.keys())
    }

# Helper functions for container management

async def _spawn_ceo_container(startup_id: str, design_doc: Dict[str, Any], app_name: str) -> Dict[str, Any]:
    """
    Spawn a dedicated persistent CEO container for a startup.
    This creates a new Modal app specifically for this CEO.
    """

    # For now, return mock data
    # TODO: Implement actual container spawning using Modal's programmatic API
    print(f"🏗️ Spawning CEO container with app name: {app_name}")

    # This would create a new Modal app with persistent container
    container_url = f"https://jakowiren--{app_name}-chat.modal.run"

    return {
        "container_url": container_url,
        "init_result": {
            "message": f"CEO container created for {startup_id}",
            "status": "ready"
        }
    }

async def _forward_to_ceo_container(container_info: Dict[str, Any], message: str) -> Dict[str, Any]:
    """
    Forward chat message to the specific CEO container.
    """
    print(f"📤 Forwarding message to container: {container_info['container_url']}")

    # TODO: Make actual HTTP request to the CEO container
    # For now, return mock response
    return {
        "response": f"[CEO Response] Thanks for your message: '{message}'. I'm working on the project!"
    }

async def _get_container_status(container_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed status from a CEO container.
    """
    print(f"📊 Checking status of container: {container_info['app_name']}")

    # TODO: Query actual container status
    return {
        "container_status": "sleeping",
        "last_activity": container_info.get("created_at"),
        "uptime": "persistent"
    }

if __name__ == "__main__":
    print("🚀 CEO Manager ready for deployment")
    print("This service manages persistent CEO containers, one per startup")
    print("Deploy with: modal deploy ceo_manager.py")