# My-YC Scaling Architecture

This document outlines how to scale the my-yc platform from the current MVP to a fully autonomous agent ecosystem.

## 🎯 Vision

**Current**: Jason AI → Design Doc → GitHub Repo (one-shot)
**Target**: Jason AI → Design Doc → CEO Agent in Container → Autonomous Team → Continuous Development

## 📦 Modal Deployment Strategies

### Current Approach: Monolithic Deployment
```bash
# Deploy entire codebase to Modal
modal deploy startup_container.py
```

**How it works:**
- Modal packages all local Python files
- Creates container images with your code
- Deploys to Modal's infrastructure
- Code lives in your repo, Modal just runs it

**Pros:** Simple, all code in one place
**Cons:** Updates affect all containers

### Phase 1: Simple Monolithic (Current Implementation)
```
backend/agents/
├── startup_container.py    # Modal container entry point
├── ceo_agent.py            # CEO agent logic
├── langchain_config.py     # LangChain setup
├── tools/
│   ├── github_tools.py     # GitHub operations
│   ├── code_generation.py  # Code writing
│   └── file_system.py      # File operations
└── prompts/
    ├── ceo_system.py       # System prompts
    └── reasoning.py        # Chain-of-thought
```

**Deployment:**
```bash
cd backend/agents
modal deploy startup_container.py
```

### Phase 2: Shared Library Architecture
```
my-yc/
├── backend/agents/
│   └── startup_container.py  # Minimal container
├── shared/                   # Shared across containers
│   ├── langchain_tools/
│   ├── prompts/
│   └── mcp_tools/
└── configs/                  # Per-startup configs
    └── startup_{id}.json
```

**Benefits:**
- Shared tools across containers
- Can update tools without rebuilding
- Each container can have different versions

### Phase 3: Dynamic Tool Loading
```python
class StartupContainer:
    def __init__(self, startup_id):
        # Load tools based on startup needs
        config = fetch_startup_config(startup_id)
        self.tools = self.load_tools(config.required_tools)

    def load_tools(self, tool_list):
        # Dynamically import tools
        tools = []
        for tool_name in tool_list:
            module = importlib.import_module(f"tools.{tool_name}")
            tools.append(module.create_tool())
        return tools
```

## 🏗️ CEO Agent Architecture

### Core Components

#### 1. CEO Agent (`ceo_agent.py`)
```python
class CEOAgent:
    def __init__(self, startup_id, design_doc):
        self.startup_id = startup_id
        self.design_doc = design_doc
        self.openai_client = OpenAI()
        self.tools = self.initialize_tools()
        self.conversation_history = []

    def initialize_tools(self):
        # Based on design doc, determine needed tools
        tools = []
        if self.needs_frontend():
            tools.append(FrontendTool())
        if self.needs_backend():
            tools.append(BackendTool())
        return tools

    async def chat(self, message):
        # Handle user communication
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                *self.conversation_history,
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content

    def get_system_prompt(self):
        return f"""You are the CEO of a startup based on this design document:
        {json.dumps(self.design_doc, indent=2)}

        Your responsibilities:
        1. Understand the project deeply
        2. Create and manage the GitHub repository
        3. Plan and coordinate development team
        4. Communicate with the founder (user)
        5. Make strategic decisions about implementation

        Available tools: {[tool.name for tool in self.tools]}
        """
```

#### 2. Startup Container (`startup_container.py`)
```python
import modal

app = modal.App("my-yc-startup")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai>=1.0.0",
    "langchain>=0.1.0",
    "PyGithub>=1.59.0",
    "fastapi>=0.100.0"
)

@app.cls(
    image=image,
    cpu=2,
    memory=4096,
    timeout=3600,
    volumes={"/workspace": modal.Volume.from_name("startup-workspace")},
    secrets=[modal.Secret.from_name("my-yc-secrets")],
    schedule=modal.Cron("*/10 * * * *")  # Keep alive
)
class StartupContainer:
    def __init__(self):
        self.ceo = None
        self.startup_id = None

    @modal.enter()
    def startup(self):
        # Initialize when container starts
        print("🏗️ Startup container initializing...")

    @modal.method()
    async def initialize(self, startup_id: str, design_doc: dict):
        """Initialize CEO with design document"""
        self.startup_id = startup_id
        self.ceo = CEOAgent(startup_id, design_doc)
        await self.ceo.initialize_project()
        return {"status": "initialized", "startup_id": startup_id}

    @modal.web_endpoint(method="POST")
    async def chat(self, request):
        """Chat with CEO"""
        data = await request.json()
        if not self.ceo:
            return {"error": "CEO not initialized"}
        response = await self.ceo.chat(data["message"])
        return {"response": response}

    @modal.web_endpoint(method="GET")
    async def status(self):
        """Get startup status"""
        if not self.ceo:
            return {"status": "not_initialized"}
        return await self.ceo.get_status()

    @modal.method()
    async def keep_alive(self):
        """Scheduled function to keep container alive"""
        if self.ceo:
            await self.ceo.perform_scheduled_tasks()
        return {"status": "alive", "timestamp": datetime.now().isoformat()}
```

## 🔧 LangChain Integration

### Basic Setup (`langchain_config.py`)
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def create_ceo_agent_executor(design_doc):
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    tools = [
        Tool(
            name="github_create_repo",
            description="Create GitHub repository",
            func=github_create_repository
        ),
        Tool(
            name="write_code",
            description="Generate and write code files",
            func=generate_code_file
        ),
        Tool(
            name="run_tests",
            description="Execute tests",
            func=run_test_suite
        ),
        Tool(
            name="plan_team",
            description="Analyze needs and plan agent team",
            func=plan_agent_team
        )
    ]

    prompt = PromptTemplate.from_template("""
    You are the CEO of a startup. Your design document is:
    {design_doc}

    User message: {input}

    Think step by step about what actions to take.
    You have access to these tools: {tools}

    {agent_scratchpad}
    """)

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def github_create_repository(name: str, description: str) -> str:
    """Create GitHub repository using PyGithub"""
    # Implementation here
    pass

def generate_code_file(filename: str, content: str) -> str:
    """Write code to file in workspace"""
    # Implementation here
    pass

def plan_agent_team(project_requirements: str) -> str:
    """Analyze project and plan needed agents"""
    # Implementation here
    pass
```

### Tool Categories

#### Development Tools
- **GitHub Tools**: Repo creation, file management, PRs
- **Code Generation**: Write components, APIs, tests
- **File System**: Create project structure
- **Package Management**: Install dependencies

#### Analysis Tools
- **Design Analysis**: Parse and understand requirements
- **Technology Selection**: Choose frameworks and tools
- **Team Planning**: Decide which agents to spawn

#### Communication Tools
- **User Interface**: Chat with founder
- **Progress Reporting**: Status updates
- **Documentation**: Generate docs and README

## 🗄️ Database Schema Evolution

### Current Schema
```sql
-- Existing MVP schema
startups (
    id UUID PRIMARY KEY,
    user_id UUID,
    title TEXT,
    design_doc JSONB,
    project_status TEXT,
    github_url TEXT,
    ...
)
```

### CEO Enhancement
```sql
-- Add CEO-specific fields
ALTER TABLE startups ADD COLUMN container_endpoint TEXT;
ALTER TABLE startups ADD COLUMN ceo_status TEXT DEFAULT 'not_spawned';
ALTER TABLE startups ADD COLUMN team_plan JSONB;
ALTER TABLE startups ADD COLUMN last_activity TIMESTAMP DEFAULT NOW();

-- CEO conversations (separate from Jason)
CREATE TABLE ceo_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'ceo')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent team tracking (future)
CREATE TABLE startup_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_id UUID REFERENCES startups(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL,
    agent_status TEXT DEFAULT 'planned',
    capabilities JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Deployment Workflow

### Development Process
```bash
# 1. Develop locally
cd backend/agents
python -m pytest tests/

# 2. Test with Modal
modal run startup_container.py::test_ceo

# 3. Deploy to Modal
modal deploy startup_container.py

# 4. Update frontend to use new endpoints
npm run build
vercel deploy
```

### Environment Management
```bash
# Modal secrets
modal secret create my-yc-secrets \
    OPENAI_API_KEY=sk-... \
    GITHUB_TOKEN=ghp_... \
    SUPABASE_URL=https://... \
    SUPABASE_SERVICE_ROLE_KEY=...

# Update secrets
modal secret update my-yc-secrets OPENAI_API_KEY=new-key
```

## 📈 Scaling Phases

### Phase 1: Basic CEO (Current Goal)
- Single CEO agent per startup
- Basic GitHub repo creation
- Simple chat interface
- Team planning (written to README)

### Phase 2: Worker Agents
- CEO can spawn specialized agents
- Frontend Agent, Backend Agent, Test Agent
- Agents report to CEO
- CEO coordinates work

### Phase 3: Autonomous Development
- Agents work independently
- Code generation and testing
- Automated deployments
- Self-improving capabilities

### Phase 4: Multi-Startup Management
- Portfolio view for users
- Cross-startup learning
- Resource optimization
- Advanced orchestration

## 🔑 Key Design Decisions

### Container Lifecycle
- **Persistent**: Containers stay alive between interactions
- **Scheduled**: Cron jobs keep containers active
- **Volume Storage**: Persistent workspace for each startup

### Communication Patterns
- **Synchronous**: Direct HTTP calls for chat
- **Asynchronous**: Background tasks for development
- **Event-Driven**: Database triggers for status updates

### Tool Architecture
- **Modular**: Each tool is independent
- **Composable**: CEO assembles tools as needed
- **Extensible**: Easy to add new capabilities

## 📊 Performance Considerations

### Modal Costs
- **CPU**: 2 cores per startup container
- **Memory**: 4GB per container
- **Storage**: Persistent volumes for workspace
- **Scheduled**: Keep-alive functions

### Optimization Strategies
- **Hibernation**: Sleep containers when inactive
- **Resource Sharing**: Common tools in shared volumes
- **Lazy Loading**: Load tools only when needed

## 🔮 Future Enhancements

### Advanced Agent Capabilities
- **Learning**: Agents improve from experience
- **Collaboration**: Multi-agent problem solving
- **Specialization**: Domain-specific agent types

### Platform Features
- **Marketplace**: Share successful agents
- **Templates**: Pre-built startup templates
- **Analytics**: Performance tracking across portfolio

This scaling strategy provides a clear path from simple MVP to sophisticated autonomous agent ecosystem while maintaining architectural flexibility.