"""
Startup Container - Persistent Modal container hosting CEO Agent
Replaces modal_spawner.py with autonomous CEO agent capabilities
"""

import modal
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

app = modal.App("my-yc-ceo")

# Container image with all dependencies including CEO agent
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai>=1.0.0",
    "PyGithub>=1.59.0",
    "fastapi>=0.100.0",
    "uvicorn>=0.20.0"
).add_local_file(
    local_path="ceo_agent.py",
    remote_path="/root/ceo_agent.py"
)

# CEO Agent will be imported from the mounted file

@app.cls(
    image=image,
    cpu=2,
    memory=4096,
    timeout=3600,
    volumes={"/data": modal.Volume.from_name("startup-workspace")},
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    min_containers=1,  # Keep one container warm
    scaledown_window=600  # 10 minutes idle timeout
)
class StartupContainer:
    """
    Persistent Modal container that hosts a CEO Agent for each startup.

    The CEO agent lives inside this container and manages the startup autonomously:
    - Creates GitHub repositories
    - Plans development teams
    - Communicates with founders
    - Coordinates development activities
    """

    def __enter__(self):
        self.ceo = None
        self.startup_id: Optional[str] = None
        self.initialized_at: Optional[str] = None
        self.last_activity: Optional[str] = None

    @modal.enter()
    def startup_enter(self):
        """Initialize when container starts"""
        print("🏗️ Startup container initializing...")
        print(f"📍 Working directory: {os.getcwd()}")

        # Add /root to Python path so we can import ceo_agent
        import sys
        sys.path.insert(0, "/root")

        print(f"🔑 Environment variables loaded")
        print(f"📁 CEO agent mounted at /root/ceo_agent.py")

    @modal.method()
    async def initialize_ceo(self, startup_id: str, design_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize CEO agent with design document.
        Called remotely by Supabase edge function.
        """
        return await self._initialize_internal(startup_id, design_doc)

    @modal.method()
    async def _initialize_internal(self, startup_id: str, design_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize CEO agent with design document.
        This creates the autonomous CEO for this startup.

        Args:
            startup_id: Unique identifier for the startup
            design_doc: Structured design document from Jason AI

        Returns:
            Initialization result including repo URL if successful
        """
        try:
            print(f"🤖 Initializing CEO for startup: {startup_id}")

            self.startup_id = startup_id
            self.initialized_at = datetime.now().isoformat()
            self.last_activity = self.initialized_at

            # Import and create CEO agent from mounted file
            from ceo_agent import CEOAgent
            self.ceo = CEOAgent(startup_id, design_doc)

            # Let CEO initialize the project autonomously
            init_result = await self.ceo.initialize_project()

            print(f"✅ CEO initialization complete: {init_result['status']}")

            return {
                **init_result,
                "container_initialized_at": self.initialized_at,
                "container_status": "ready"
            }

        except Exception as e:
            print(f"❌ CEO initialization failed: {str(e)}")
            return {
                "success": False,
                "error": f"CEO initialization failed: {str(e)}",
                "container_status": "error"
            }

    @modal.fastapi_endpoint(method="POST", label="chat")
    async def chat_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chat with the CEO agent.
        This is how founders communicate with their startup's CEO.

        Expected payload:
        {
            "message": "How is development progressing?",
            "startup_id": "uuid-here"  # Optional verification
        }
        """
        try:
            if not self.ceo:
                return {
                    "success": False,
                    "error": "CEO not initialized. Initialize the startup first."
                }

            message = request_data.get("message", "")
            if not message.strip():
                return {
                    "success": False,
                    "error": "Message is required"
                }

            print(f"💬 Founder message: {message[:100]}...")

            # Update activity timestamp
            self.last_activity = datetime.now().isoformat()

            # Get CEO response
            ceo_response = await self.ceo.chat(message)

            return {
                "success": True,
                "response": ceo_response,
                "startup_id": self.startup_id,
                "timestamp": self.last_activity
            }

        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
            return {
                "success": False,
                "error": f"Chat failed: {str(e)}"
            }

    @modal.fastapi_endpoint(method="GET", label="status")
    async def status_endpoint(self) -> Dict[str, Any]:
        """
        Get current status of the startup and CEO agent.
        """
        try:
            if not self.ceo:
                return {
                    "container_status": "not_initialized",
                    "startup_id": None,
                    "ceo_status": None,
                    "initialized_at": None,
                    "last_activity": None
                }

            # Get detailed status from CEO
            ceo_status = await self.ceo.get_status()

            return {
                "container_status": "running",
                "startup_id": self.startup_id,
                "initialized_at": self.initialized_at,
                "last_activity": self.last_activity,
                "ceo_status": ceo_status
            }

        except Exception as e:
            print(f"❌ Status error: {str(e)}")
            return {
                "container_status": "error",
                "error": str(e)
            }

    @modal.method()
    async def perform_scheduled_tasks(self) -> Dict[str, Any]:
        """
        Scheduled maintenance and development tasks.
        Called periodically to keep the CEO active and working.
        """
        try:
            if not self.ceo:
                return {
                    "status": "no_ceo",
                    "message": "CEO not initialized"
                }

            print(f"⏰ Running scheduled tasks for startup: {self.startup_id}")

            # Update activity timestamp
            self.last_activity = datetime.now().isoformat()

            # Let CEO perform its scheduled work
            task_result = await self.ceo.perform_scheduled_tasks()

            return {
                "status": "completed",
                "startup_id": self.startup_id,
                "last_activity": self.last_activity,
                "ceo_tasks": task_result
            }

        except Exception as e:
            print(f"❌ Scheduled tasks error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    @modal.method()
    async def get_conversation_history(self) -> Dict[str, Any]:
        """
        Get the conversation history between founder and CEO.
        """
        try:
            if not self.ceo:
                return {
                    "success": False,
                    "error": "CEO not initialized"
                }

            return {
                "success": True,
                "startup_id": self.startup_id,
                "conversation_history": self.ceo.conversation_history,
                "message_count": len(self.ceo.conversation_history)
            }

        except Exception as e:
            print(f"❌ Conversation history error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Scheduled function to keep containers alive and CEOs working
@app.function(
    image=image,
    schedule=modal.Cron("*/10 * * * *"),  # Every 10 minutes
    secrets=[modal.Secret.from_name("my-yc-secrets")]
)
async def keep_containers_alive():
    """
    Scheduled function to keep startup containers active.
    This ensures CEOs continue their work even when not chatting.
    """
    print("🔄 Running container keep-alive check...")

    # Note: In a real implementation, this would:
    # 1. Query Supabase for active startups
    # 2. Call perform_scheduled_tasks on each container
    # 3. Update container status in database

    # For now, just log that we're keeping things alive
    print(f"✅ Keep-alive check completed at {datetime.now().isoformat()}")

    return {
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }

# Test function for development
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")]
)
async def test_ceo_initialization():
    """
    Test function to verify CEO can create GitHub repos.
    This is the key test point for CEO autonomy.
    """
    print("🧪 Testing CEO GitHub repository creation...")

    # Sample design document for testing
    test_design_doc = {
        "title": "AI-Powered Task Manager",
        "executive_summary": "A smart task management app that uses AI to prioritize and organize work",
        "problem_statement": "People struggle to manage their daily tasks effectively",
        "target_market": "Busy professionals and students",
        "value_proposition": "AI-driven task prioritization saves time and reduces stress",
        "mvp_features": [
            "Task creation and management",
            "AI-powered priority scoring",
            "Smart scheduling suggestions",
            "Progress tracking"
        ],
        "tech_stack": [
            "React Native for mobile app",
            "Node.js backend",
            "PostgreSQL database",
            "OpenAI API for AI features"
        ],
        "success_metrics": [
            "Daily active users",
            "Task completion rate",
            "User retention"
        ]
    }

    # Create test startup ID
    test_startup_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        # Import CEO agent from mounted file
        import sys
        sys.path.insert(0, "/root")
        from ceo_agent import CEOAgent

        ceo = CEOAgent(test_startup_id, test_design_doc)

        # Test CEO initialization (should create GitHub repo)
        result = await ceo.initialize_project()

        print(f"🎉 Test result: {result}")

        return {
            "test_status": "success",
            "startup_id": test_startup_id,
            "github_created": result.get("success", False),
            "repo_url": result.get("repo_url"),
            "message": result.get("message", "Test completed")
        }

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return {
            "test_status": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    # For local testing
    print("🚀 Startup Container ready for deployment to Modal")
    print("Deploy with: modal deploy startup_container.py")