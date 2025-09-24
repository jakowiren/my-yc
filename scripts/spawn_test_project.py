#!/usr/bin/env python3
"""
Test script for spawning a project locally.
Usage: python scripts/spawn_test_project.py "Your startup idea"
"""

import sys
import asyncio
import uuid
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

async def test_spawn_project(idea_title: str):
    """Test the project spawning process locally."""

    project_id = str(uuid.uuid4())
    project_config = {
        "title": idea_title,
        "description": f"A startup focused on {idea_title.lower()}",
        "category": "tech",
        "target_market": "early adopters"
    }

    print(f"🧪 Testing project spawn for: {idea_title}")
    print(f"📋 Project ID: {project_id}")
    print(f"⚙️  Config: {project_config}")

    try:
        # Import modal spawner
        from modal_spawner import spawn_project

        # Test spawning
        result = spawn_project.remote(project_id, project_config)
        print(f"✅ Spawn result: {result}")

        # Wait a bit and check status
        await asyncio.sleep(5)

        from modal_spawner import get_project_status
        status = get_project_status.remote(project_id)
        print(f"📊 Project status: {status}")

    except ImportError:
        print("⚠️  Modal not available, testing orchestrator API instead...")

        # Test with orchestrator API directly
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/projects/spawn",
                json={
                    "title": idea_title,
                    "description": project_config["description"],
                    "category": project_config["category"],
                    "target_market": project_config["target_market"]
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Spawn result: {result}")

                # Check status
                project_id = result["project_id"]
                status_response = await client.get(f"http://localhost:8000/projects/{project_id}")

                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 API Project status: {status}")
                else:
                    print(f"❌ Failed to get status: {status_response.status_code}")
            else:
                print(f"❌ API request failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error during test: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/spawn_test_project.py 'Your startup idea'")
        print("Example: python scripts/spawn_test_project.py 'AI recipe recommender'")
        sys.exit(1)

    idea_title = sys.argv[1]
    asyncio.run(test_spawn_project(idea_title))

if __name__ == "__main__":
    main()