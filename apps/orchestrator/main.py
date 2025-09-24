"""
my-yc Orchestrator API
Main FastAPI application for managing project spawning and orchestration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import asyncio

app = FastAPI(
    title="my-yc Orchestrator",
    description="AI-powered startup incubator orchestration API",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ProjectIdea(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    target_market: Optional[str] = None

class ProjectStatus(BaseModel):
    project_id: str
    status: str  # "spawning", "running", "sleeping", "error"
    progress: float  # 0-100
    current_task: Optional[str] = None
    agents_active: List[str] = []
    created_at: str
    last_updated: str

class SpawnResponse(BaseModel):
    project_id: str
    message: str
    status: str

# In-memory storage for demo (replace with database)
projects: Dict[str, ProjectStatus] = {}

@app.get("/")
async def root():
    return {"message": "my-yc Orchestrator API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator"}

@app.post("/projects/spawn", response_model=SpawnResponse)
async def spawn_project(idea: ProjectIdea):
    """Spawn a new autonomous startup project."""
    project_id = str(uuid.uuid4())

    # Create project record
    project_status = ProjectStatus(
        project_id=project_id,
        status="spawning",
        progress=0,
        current_task="Initializing project container",
        agents_active=[],
        created_at=str(asyncio.get_event_loop().time()),
        last_updated=str(asyncio.get_event_loop().time())
    )

    projects[project_id] = project_status

    # TODO: Actually spawn Modal/Fly container here
    # For now, simulate the spawning process
    asyncio.create_task(simulate_project_lifecycle(project_id, idea))

    return SpawnResponse(
        project_id=project_id,
        message=f"Project '{idea.title}' spawning initiated",
        status="spawning"
    )

@app.get("/projects", response_model=List[ProjectStatus])
async def list_projects():
    """List all projects in the portfolio."""
    return list(projects.values())

@app.get("/projects/{project_id}", response_model=ProjectStatus)
async def get_project(project_id: str):
    """Get specific project status."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id]

@app.delete("/projects/{project_id}")
async def terminate_project(project_id: str):
    """Terminate and cleanup a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Actually terminate Modal/Fly container
    del projects[project_id]
    return {"message": f"Project {project_id} terminated"}

async def simulate_project_lifecycle(project_id: str, idea: ProjectIdea):
    """Simulate the project lifecycle for demo purposes."""
    project = projects[project_id]

    stages = [
        ("Analyzing market opportunity", 10),
        ("Designing product architecture", 25),
        ("Generating frontend with Lovable", 45),
        ("Provisioning Supabase database", 65),
        ("Deploying to Vercel", 80),
        ("Setting up payment processing", 90),
        ("Project launch complete", 100),
    ]

    for task, progress in stages:
        await asyncio.sleep(2)  # Simulate work time
        project.current_task = task
        project.progress = progress
        project.last_updated = str(asyncio.get_event_loop().time())

        if progress == 100:
            project.status = "sleeping"
            project.current_task = "Autonomous operation (container sleeping)"
            project.agents_active = []
        else:
            project.agents_active = ["coordinator", "business_analyst"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)