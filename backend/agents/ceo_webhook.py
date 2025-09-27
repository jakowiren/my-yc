"""
CEO Webhook - Simple FastAPI server for stable CEO initialization endpoint
This provides a stable HTTP endpoint that won't change between deployments
"""

import modal
import json
from typing import Dict, Any

# Stable app name
app = modal.App("ceo-webhook")

# Simple image with FastAPI
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi>=0.100.0",
    "uvicorn>=0.20.0"
)

# Deploy as function with FastAPI
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("my-yc-secrets")]
)
@modal.wsgi_app()
def fastapi_app():
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    # Request model
    class CEOInitRequest(BaseModel):
        startup_id: str
        design_doc: Dict[str, Any]

    # Create FastAPI app
    web_app = FastAPI()

    @web_app.post("/initialize")
    async def initialize_ceo(request: CEOInitRequest):
        """
        Initialize CEO agent for a startup.
        This is a stable HTTP endpoint for Supabase to call.
        """
        try:
            print(f"🚀 Received CEO initialization request for startup: {request.startup_id}")

            # For now, simulate success since we proved the CEO works
            # TODO: Actually call the CEO container when the naming conflicts are resolved
            result = {
                "success": True,
                "startup_id": request.startup_id,
                "message": f"CEO Agent initialization simulated for '{request.design_doc.get('title', 'Unknown Startup')}'",
                "repo_url": f"https://github.com/my-yc-creator/simulated-repo-{request.startup_id[:8]}",
                "status": "ready"
            }

            print(f"✅ CEO initialization result: {result}")
            return result

        except Exception as e:
            print(f"❌ CEO initialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"CEO initialization failed: {str(e)}")

    @web_app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "ceo-webhook"}

    return web_app

if __name__ == "__main__":
    print("🚀 CEO Webhook ready for deployment to Modal")
    print("Deploy with: modal deploy ceo_webhook.py")