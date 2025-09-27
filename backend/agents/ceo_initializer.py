"""
CEO Initializer - Stable Modal function for initializing CEO agents
This provides a stable endpoint that won't change between deployments
"""

import modal
import json
from typing import Dict, Any

app = modal.App("ceo-initializer")

# Simple image just for calling the main CEO container
image = modal.Image.debian_slim(python_version="3.11").pip_install("modal")

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    timeout=300
)
async def initialize_ceo_for_startup(startup_id: str, design_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stable function to initialize CEO agents.
    This calls the main CEO container to do the actual work.

    This function has a stable URL that won't change between deployments.
    """
    print(f"🚀 Initializing CEO for startup: {startup_id}")

    try:
        # Import modal inside the function to avoid issues
        import modal

        # Get reference to the main CEO container app
        ceo_app = modal.App.lookup("my-yc-ceo", create_if_missing=False)
        startup_container = ceo_app["StartupContainer"]

        # Call the CEO initialization
        result = await startup_container.initialize_ceo.remote(startup_id, design_doc)

        print(f"✅ CEO initialization result: {result}")
        return result

    except Exception as e:
        print(f"❌ CEO initialization failed: {str(e)}")
        return {
            "success": False,
            "error": f"CEO initialization failed: {str(e)}",
            "startup_id": startup_id
        }

if __name__ == "__main__":
    print("🚀 CEO Initializer ready for deployment to Modal")
    print("Deploy with: modal deploy ceo_initializer.py")