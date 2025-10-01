"""
Startup Workspace Container - One container per startup hosting multiple LLM agents
Replaces the expensive CEO-only containers with a cost-effective shared workspace model.
Cost: ~$1/month per startup vs $90/month with persistent memory across all agents.
"""

import modal
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

# SHARED app name - all startups use this app, containers differentiated by startup_id
app = modal.App("my-yc-startup-workspaces")

# Persistent volume for all startup workspaces
startup_workspaces = modal.Volume.from_name("startup-workspaces", create_if_missing=True)

# Optimized container image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai>=1.0.0",
    "PyGithub>=1.59.0",
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
    "gitpython>=3.1.0"
).add_local_file(
    local_path="agent_orchestrator.py",
    remote_path="/root/agent_orchestrator.py"
).add_local_file(
    local_path="agent_configs.py",
    remote_path="/root/agent_configs.py"
).add_local_file(
    local_path="workspace_manager.py",
    remote_path="/root/workspace_manager.py"
).add_local_dir(
    local_path="mcp_tools",
    remote_path="/root/mcp_tools"
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=300,
    cpu=1.0,  # Reduced from 2 CPU
    memory=2048,  # Reduced from 4096 MB
    # NO min_containers! Allow cold starts to save money
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="POST", label="workspace-initialize")
async def initialize_workspace(request_data: Dict[str, Any]):
    """
    Initialize workspace for a startup with all agent infrastructure.
    Endpoint: https://jakowiren--my-yc-startup-workspaces-initialize.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from workspace_manager import WorkspaceManager
        from agent_orchestrator import AgentOrchestrator

        startup_id = request_data.get("startup_id")
        design_doc = request_data.get("design_doc")

        if not startup_id or not design_doc:
            return {
                "success": False,
                "error": "startup_id and design_doc are required"
            }

        print(f"🏗️ Initializing workspace for startup: {startup_id}")
        startup_name = design_doc.get("title", f"Startup {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace already exists
        if workspace_mgr.workspace_exists(startup_id):
            print(f"📁 Workspace already exists for {startup_id}")
            workspace_info = workspace_mgr.get_workspace_info(startup_id)
            result = {
                "success": True,
                "startup_id": startup_id,
                "status": "resumed",
                "message": f"Workspace resumed for '{startup_name}'",
                "workspace_info": workspace_info,
                "container_status": "warm",
                "available_agents": ["ceo", "frontend", "backend", "design", "testing"]
            }
        else:
            print(f"🏗️ Creating new workspace for {startup_id}")
            # Initialize workspace with multi-agent support
            workspace_path = workspace_mgr.initialize_workspace(startup_id, startup_name, design_doc)

            # Initialize agent orchestrator
            orchestrator = AgentOrchestrator(startup_id, workspace_mgr)

            # Initialize CEO agent (primary agent)
            await orchestrator.initialize_agent("ceo", design_doc)

            result = {
                "success": True,
                "startup_id": startup_id,
                "status": "initialized",
                "message": f"Workspace created for '{startup_name}'",
                "workspace_path": str(workspace_path),
                "container_status": "cold_start",
                "available_agents": ["ceo", "frontend", "backend", "design", "testing"],
                "cold_start_time": datetime.now().isoformat()
            }

        # Update workspace activity
        workspace_mgr.update_last_activity(startup_id)

        print(f"✅ Workspace initialization complete: {result}")
        return result

    except Exception as e:
        print(f"❌ Workspace initialization failed: {str(e)}")
        return {
            "success": False,
            "error": f"Workspace initialization failed: {str(e)}",
            "startup_id": request_data.get("startup_id")
        }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=120,
    cpu=1.0,
    memory=2048,
    # NO min_containers!
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="POST", label="workspace-agent-invoke")
async def invoke_agent(request_data: Dict[str, Any]):
    """
    Universal agent invocation endpoint - routes to any agent type.
    Endpoint: https://jakowiren--my-yc-startup-workspaces-agent-invoke.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from workspace_manager import WorkspaceManager
        from agent_orchestrator import AgentOrchestrator

        startup_id = request_data.get("startup_id")
        agent_type = request_data.get("agent_type", "ceo")  # Default to CEO
        message = request_data.get("message")
        context = request_data.get("context", {})

        if not startup_id or not message:
            return {
                "success": False,
                "error": "startup_id and message are required"
            }

        print(f"🤖 Agent invocation: {agent_type} for startup {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace exists
        if not workspace_mgr.workspace_exists(startup_id):
            return {
                "success": False,
                "error": "Workspace not initialized for this startup. Please initialize first.",
                "agent_type": agent_type,
                "startup_id": startup_id
            }

        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(startup_id, workspace_mgr)

        # Invoke the specified agent
        response = await orchestrator.invoke_agent(
            agent_type=agent_type,
            message=message,
            context=context
        )

        # Update workspace activity
        workspace_mgr.update_last_activity(startup_id)

        return {
            "success": True,
            "agent_type": agent_type,
            "startup_id": startup_id,
            "response": response.get("content", ""),
            "tools_used": response.get("tools_used", []),
            "container_status": "active",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Agent invocation failed: {str(e)}")
        return {
            "success": False,
            "error": f"Agent invocation failed: {str(e)}",
            "agent_type": request_data.get("agent_type", "unknown"),
            "startup_id": request_data.get("startup_id")
        }

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=120,
    cpu=1.0,
    memory=2048,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="POST", label="workspace-agent-stream")
async def invoke_agent_streaming(request_data: Dict[str, Any]):
    """
    Streaming agent invocation for real-time chat experience.
    Endpoint: https://jakowiren--workspace-agent-stream.modal.run
    """
    print(f"🎬 STREAMING ENDPOINT CALLED")
    print(f"🎬 Request data: {request_data}")

    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from workspace_manager import WorkspaceManager
        from agent_orchestrator import AgentOrchestrator
        from fastapi.responses import StreamingResponse

        startup_id = request_data.get("startup_id")
        agent_type = request_data.get("agent_type", "ceo")
        message = request_data.get("message")

        print(f"🎬 Parsed: startup_id={startup_id}, agent_type={agent_type}, message={message[:50] if message else None}")

        if not startup_id or not message:
            print(f"❌ Missing required fields: startup_id={startup_id}, message={bool(message)}")
            return {
                "success": False,
                "error": "startup_id and message are required"
            }

        print(f"💬 Streaming agent: {agent_type} for startup {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        # Check if workspace exists
        print(f"🎬 Checking if workspace exists for {startup_id}")
        if not workspace_mgr.workspace_exists(startup_id):
            print(f"❌ Workspace not found for {startup_id}")
            return {
                "success": False,
                "error": "Workspace not initialized for this startup. Please initialize first."
            }
        print(f"✅ Workspace exists for {startup_id}")

        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(startup_id, workspace_mgr)

        async def generate_stream():
            """Generate Server-Sent Events stream."""
            try:
                async for chunk in orchestrator.invoke_agent_streaming(
                    agent_type=agent_type,
                    message=message
                ):
                    chunk_type = chunk.get("type", "content")
                    content = chunk.get("content", "")

                    if chunk_type == "content" and content:
                        # Send content chunks
                        yield f"data: {json.dumps({'content': content, 'agent': agent_type})}\n\n"
                    elif chunk_type == "tool_execution":
                        # Send tool execution updates
                        yield f"data: {json.dumps({'tool_status': content, 'agent': agent_type})}\n\n"

                # Send completion signal
                yield f"data: [DONE]\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'agent': agent_type})}\n\n"

        # Update workspace activity
        workspace_mgr.update_last_activity(startup_id)

        print(f"🎬 Returning StreamingResponse for {startup_id}")
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

    except Exception as e:
        print(f"❌ Streaming agent failed: {str(e)}")
        return {
            "success": False,
            "error": f"Streaming agent failed: {str(e)}"
        }

@app.function(
    image=image,
    timeout=30,
    cpu=0.5,  # Very minimal resources for status checks
    memory=512,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="GET", label="workspace-status-check")
async def get_workspace_status(startup_id: str):
    """
    Get workspace status and information.
    Endpoint: https://jakowiren--my-yc-startup-workspaces-workspace-status.modal.run
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
                "status": "not_initialized",
                "message": "Workspace not found. Please initialize first.",
                "container_status": "cold"
            }

        # Get workspace info
        workspace_info = workspace_mgr.get_workspace_info(startup_id)

        # Get available agents
        available_agents = ["ceo", "frontend", "backend", "design", "testing"]

        # Check team message board
        team_messages = workspace_mgr.get_team_messages(startup_id) if hasattr(workspace_mgr, 'get_team_messages') else []

        return {
            "startup_id": startup_id,
            "status": workspace_info.get("ceo_status", "unknown"),
            "workspace_path": workspace_info.get("workspace_path"),
            "last_activity": workspace_info.get("last_activity"),
            "conversation_count": workspace_info.get("conversation_count", 0),
            "available_agents": available_agents,
            "team_messages_count": len(team_messages),
            "container_status": "active",
            "metadata": workspace_info.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        return {
            "startup_id": startup_id,
            "status": "error",
            "error": str(e),
            "container_status": "unknown"
        }

@app.function(
    image=image,
    timeout=30,
    cpu=0.5,
    memory=512,
    volumes={"/workspace": startup_workspaces}
)
@modal.fastapi_endpoint(method="GET", label="workspace-team-board")
async def get_team_board(startup_id: str):
    """
    Get team message board for testing persistence.
    Endpoint: https://jakowiren--my-yc-startup-workspaces-team-board.modal.run
    """
    try:
        # Import modules inside the function
        import sys
        sys.path.insert(0, "/root")
        from workspace_manager import WorkspaceManager

        print(f"📋 Team board request for startup: {startup_id}")

        # Initialize workspace manager
        workspace_mgr = WorkspaceManager()

        if not workspace_mgr.workspace_exists(startup_id):
            return {
                "startup_id": startup_id,
                "messages": [],
                "error": "Workspace not found"
            }

        # Get team messages (we'll implement this in workspace_manager)
        messages = workspace_mgr.get_team_messages(startup_id) if hasattr(workspace_mgr, 'get_team_messages') else []

        return {
            "startup_id": startup_id,
            "messages": messages,
            "count": len(messages),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Team board request failed: {str(e)}")
        return {
            "startup_id": startup_id,
            "messages": [],
            "error": str(e)
        }

@app.function(
    image=image,
    timeout=10,
    cpu=0.25,
    memory=256
    # NO min_containers and minimal resources for health checks
)
@modal.fastapi_endpoint(method="GET", label="workspace-health")
async def health_check():
    """
    Health check endpoint.
    Endpoint: https://jakowiren--my-yc-startup-workspaces-health.modal.run
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
        "service": "my-yc-startup-workspaces",
        "architecture": "multi-agent-workspace",
        "active_workspaces": workspace_count,
        "cost_optimization": "cold_start_enabled",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Startup Workspace Service ready for deployment")
    print("New architecture: One container per startup, multiple agents per container")
    print("Cost optimization: Cold starts enabled, ~$1/month per startup")
    print("Endpoints:")
    print("  Initialize:  https://jakowiren--my-yc-startup-workspaces-workspace-initialize.modal.run")
    print("  Agent:       https://jakowiren--my-yc-startup-workspaces-workspace-agent-invoke.modal.run")
    print("  Stream:      https://jakowiren--my-yc-startup-workspaces-workspace-agent-stream.modal.run")
    print("  Status:      https://jakowiren--my-yc-startup-workspaces-workspace-status-check.modal.run")
    print("  Team Board:  https://jakowiren--my-yc-startup-workspaces-workspace-team-board.modal.run")
    print("  Health:      https://jakowiren--my-yc-startup-workspaces-workspace-health.modal.run")
    print("Deploy with: modal deploy startup_workspace.py")