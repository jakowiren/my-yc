# Temporal.io Migration Plan: From Modal Functions to Long-Running Autonomous Agents

## 🎯 Executive Summary

Temporal.io offers the best path to achieve true long-term autonomous agents while maintaining cost efficiency. This document outlines the case for migration and provides a detailed technical implementation plan.

## 📊 Cost Analysis Summary

### Current Architecture (Modal Functions + Volumes)
```
Cost per startup: $15/month
Agent behavior: "Diary reading" - agents reconstruct state from files
Persistence: Pseudo-persistent via file system
```

### Modal Containers (@app.cls)
```
Cost per startup: $720/month (always-on containers)
Agent behavior: True persistent consciousness
Persistence: Real - agents maintain memory across interactions
```

### Temporal.io Workflows
```
Cost per startup: $20-65/month (depending on dev vs prod namespace)
Agent behavior: True persistent consciousness + enterprise features
Persistence: Perfect - workflows can run for months/years with full state
```

### Cost Comparison Table

| Architecture | 1 Startup | 5 Startups | 20 Startups |
|--------------|-----------|------------|--------------|
| **Current Functions** | $15/month | $75/month | $300/month |
| **Modal Containers** | $720/month | $3,600/month | $14,400/month |
| **Temporal Dev** | $25/month | $125/month | $325/month |
| **Temporal Prod** | $65/month | $325/month | $525/month |

## ✅ Pros of Temporal.io Migration

### 🧠 **True Agent Consciousness**
- **Continuous memory**: Agents maintain state across months without reconstruction
- **No cold starts**: Instant response times with perfect context continuity
- **Long-term initiative**: Agents can work autonomously for weeks without human input
- **Deep learning**: Agents build institutional knowledge over time

### 💰 **Cost Efficiency**
- **2-11x cheaper** than Modal containers for persistent agents
- **Scales efficiently**: Cost grows linearly with usage, not container count
- **Development tier**: Full features at $25/month for MVP testing

### 🏗️ **Enterprise Architecture**
- **Built-in scheduling**: Native support for hourly/daily/weekly agent tasks
- **Fault tolerance**: Automatic recovery from failures with perfect state preservation
- **Audit trail**: Complete history of all agent decisions and actions
- **Multi-agent coordination**: Built-in patterns for agent teams

### 🔄 **Operational Excellence**
- **Zero infrastructure management**: No container lifecycle to manage
- **Automatic scaling**: Handles load spikes without configuration
- **Built-in monitoring**: Rich observability out of the box
- **Version management**: Safe deployment of agent logic updates

## ❌ Cons of Temporal.io Migration

### 🧑‍💻 **Development Complexity**
- **Learning curve**: 2-4 weeks to understand Temporal concepts
- **Determinism constraints**: Workflows have strict rules about what's allowed
- **Activity pattern**: All real work must happen in activities, not workflows
- **Debugging complexity**: Distributed systems debugging is harder

### 🏗️ **Architecture Overhead**
- **Complete rewrite**: Cannot incrementally migrate from current Modal functions
- **New patterns**: Requires rethinking agent architecture around workflows/activities
- **Testing complexity**: Need to test both workflow logic and activity implementations
- **Infrastructure dependency**: Platform lock-in to Temporal ecosystem

### 🔧 **Technical Constraints**
- **Workflow limitations**: No direct API calls, file access, or non-deterministic operations
- **State serialization**: All workflow state must be JSON-serializable
- **Activity timeouts**: Must configure retry policies and timeouts for all operations
- **Network calls**: All external integrations happen through activities

### 💸 **Hidden Costs**
- **Activity workers**: Need compute resources to run activity code (~$50-100/month)
- **Development time**: Significant upfront investment in migration
- **Learning investment**: Team training and ramp-up time

## 🤖 **Free-Thinking Autonomous Agents: The Challenge & Solution**

### **The Temporal Constraint Problem**

Temporal workflows have strict determinism requirements that seem to conflict with autonomous agent behavior:

```python
@workflow.defn
class CEOWorkflow:
    async def run(self):
        # ❌ FORBIDDEN - All of these break determinism:
        response = await openai.chat.completions.create(...)  # Non-deterministic
        with open("/workspace/file.txt", "r") as f: ...       # Side effects
        now = datetime.now()                                  # Non-deterministic
        choice = random.choice([1,2,3])                      # Non-deterministic
```

This creates challenges for autonomous agents that need to:
- Think creatively and spontaneously
- Explore ideas in non-linear ways
- Maintain "flow state" during deep thinking
- React to environmental changes dynamically

### **The Hybrid Solution: Meta-Cognition + Deep Thinking**

The solution is to combine **two computational models**:

#### **Model 1: Temporal Workflows (Executive Function)**
```python
@workflow.defn
class CEOWorkflow:
    """
    Handles meta-cognition:
    - WHEN to think (scheduling, triggers)
    - WHAT to remember (long-term memory)
    - HOW to coordinate (multi-agent orchestration)
    """

    def __init__(self):
        self.long_term_memory = []        # Persisted across months
        self.personality_state = {}       # Agent's evolving identity
        self.relationship_context = {}    # Memory of user interactions
        self.strategic_goals = []         # Long-term objectives

    async def run(self):
        while True:
            # Temporal excels at orchestration and scheduling

            if self.should_do_daily_reflection():
                await self.trigger_thinking_session("daily_reflection")

            if self.has_pending_user_messages():
                await self.trigger_thinking_session("user_interaction")

            if self.should_do_weekly_planning():
                await self.trigger_thinking_session("strategic_planning")

            # Agent can trigger spontaneous thinking
            if self.detected_interesting_pattern():
                await self.trigger_thinking_session("spontaneous_exploration")

    async def trigger_thinking_session(self, session_type: str):
        """Delegate actual thinking to substantial activities"""
        thinking_results = await workflow.execute_activity(
            deep_thinking_session_activity,
            args=[session_type, self.get_context()],
            start_to_close_timeout=timedelta(minutes=45),  # Long enough for deep thinking
            heartbeat_timeout=timedelta(minutes=5)         # Progress updates
        )

        # Update persistent state with thinking results
        self.long_term_memory.extend(thinking_results.insights)
        self.strategic_goals.extend(thinking_results.new_goals)
```

#### **Model 2: Substantial Activities (Creative Cognition)**
```python
@activity.defn
async def deep_thinking_session_activity(session_type: str, context: AgentContext) -> ThinkingResults:
    """
    Inside activities, agents can think completely freely:
    - Multiple OpenAI calls in sequence
    - File system exploration
    - Creative brainstorming loops
    - Spontaneous idea generation
    - Stream of consciousness reasoning
    """

    # Initialize agent with full autonomous capabilities
    agent = AutonomousAgent(context)

    if session_type == "spontaneous_exploration":
        return await creative_exploration_session(agent)
    elif session_type == "user_interaction":
        return await interactive_thinking_session(agent)
    # ... other session types

async def creative_exploration_session(agent: AutonomousAgent) -> ThinkingResults:
    """Agent can think freely for 30+ minutes without interruption"""

    session_insights = []

    # Phase 1: Environmental observation (5 minutes)
    print("🔍 Observing project environment...")
    github_state = agent.analyze_github_repository()
    user_patterns = agent.analyze_user_feedback_trends()
    code_health = agent.analyze_codebase_metrics()

    # Phase 2: Stream of consciousness analysis (20 minutes)
    print("🧠 Following interesting patterns...")
    current_thought = agent.notice_something_interesting()
    thought_chain = []

    for thinking_cycle in range(15):  # Agent can think as long as needed
        # Maintain flow state - no Temporal interruptions
        next_thought = await agent.llm_call(
            "Continue this line of thinking",
            {
                "current_thought": current_thought,
                "thought_chain": thought_chain,
                "environment": {"github": github_state, "users": user_patterns}
            }
        )

        thought_chain.append(next_thought)
        current_thought = next_thought

        # Agent can spontaneously explore tangents
        if agent.wants_to_explore_tangent(current_thought):
            tangent = await agent.explore_creative_tangent(current_thought)
            thought_chain.append(tangent)

        # Build up insights organically
        session_insights.extend(agent.extract_insights(next_thought))

    # Phase 3: Synthesis and decision making (10 minutes)
    print("💡 Synthesizing insights into actionable plans...")
    decisions = await agent.synthesize_decisions(session_insights, thought_chain)
    actions = await agent.create_implementation_plan(decisions)

    return ThinkingResults(
        insights=session_insights,
        thought_chain=thought_chain,
        decisions=decisions,
        actions=actions,
        session_type="creative_exploration",
        duration_minutes=35,
        quality_score=agent.assess_thinking_quality()
    )
```

### **Concrete Example: How This Enables True Autonomy**

```python
# Temporal Workflow (Executive Function):
"""
'I notice it's been 3 days since I reviewed user feedback.
 I also see there are 5 new GitHub issues.
 My long-term goal is to improve user retention.
 My personality trait is being proactive about user experience.
 Time to trigger a spontaneous thinking session.'
"""

# Deep Thinking Activity (Creative Cognition):
"""
'Let me spend 35 minutes really diving into these patterns...

 I'm seeing repeated complaints about mobile responsiveness.
 Looking at analytics: 67% mobile traffic, but mobile conversion is 40% lower.

 This reminds me of something I noticed last week about CSS performance...
 Let me explore that connection deeper...

 Actually, this connects to a broader insight about our architecture.
 What if we're thinking about this wrong entirely?

 Instead of fixing responsive issues, what if we went mobile-first?
 Let me think through the technical implications...
 [15 minutes of uninterrupted technical reasoning]

 This could be transformative. I should:
 1. Prototype a mobile-first CSS architecture
 2. A/B test with 10% of mobile users
 3. Coordinate with Frontend Agent on implementation
 4. Create user feedback loop for iteration'
"""

# Back to Temporal Workflow (Memory Integration):
"""
'I had breakthrough insights about mobile-first architecture.
 This aligns with my long-term goal of improving user retention.
 I'm updating my strategic memory with these insights.
 I should schedule coordination with Frontend Agent tomorrow.
 I should also plan a follow-up thinking session next week to review results.'
"""
```

### **Why This Hybrid Approach Works**

#### **Temporal Provides (Executive Function):**
- **Persistent Identity**: "I am CEO Agent #47, working on this startup for 3 months"
- **Long-term Memory**: "I remember our conversation last week about onboarding"
- **Strategic Continuity**: "This connects to my 6-month improvement goals"
- **Multi-Agent Coordination**: "I need to sync with the Frontend Agent"
- **Reliable Scheduling**: "Time for my weekly strategic review"

#### **Activities Provide (Creative Cognition):**
- **Free Thinking**: "Let me explore this interesting pattern..."
- **Flow State**: "35 minutes of uninterrupted deep thinking"
- **Spontaneous Connections**: "Wait, this reminds me of something else..."
- **Creative Exploration**: "What if we approached this completely differently?"
- **Technical Deep Dives**: "Let me really understand this codebase issue"

### **Key Benefits of This Architecture**

1. **True Autonomy**: Agents can think for extended periods without human input
2. **Creative Problem Solving**: No constraints on exploration within thinking sessions
3. **Institutional Memory**: Perfect recall of months of context and decisions
4. **Strategic Continuity**: Agents maintain long-term goals across thinking sessions
5. **Fault Tolerance**: If thinking session crashes, workflow resumes from last checkpoint
6. **Scalable**: Multiple agents can coordinate through shared Temporal orchestration

This hybrid model gives you the best of both worlds: **reliable, persistent consciousness** (Temporal) + **unlimited creative thinking** (substantial activities).

## 🏗️ **Clean Temporal + Modal Architecture**

### **Responsibility Separation**

The key to a successful Temporal + Modal integration is clean separation of concerns:

#### **Temporal's Job: Agent Consciousness & Orchestration**
```python
# Temporal manages the "soul" of each agent
@workflow.defn
class CEOWorkflow:
    """
    Temporal handles:
    - Agent identity and long-term memory
    - Strategic decision making and planning
    - Multi-agent coordination
    - Scheduling and lifecycle management
    """

    def __init__(self):
        # Agent's persistent identity (serializable state)
        self.identity = AgentIdentity(
            startup_id="",
            personality_traits={},
            long_term_goals=[],
            strategic_context={}
        )

        # Agent's memory (conversation history, decisions, insights)
        self.memory = AgentMemory(
            conversations=[],
            decisions=[],
            insights=[],
            learned_patterns={}
        )

        # Agent coordination state
        self.coordination = AgentCoordination(
            active_colleagues=[],
            shared_projects=[],
            communication_queue=[]
        )
```

#### **Modal's Job: Agent Actions & Workspace**
```python
# Modal handles the "body" and "tools" of each agent
@app.function(volumes={"/workspace": startup_workspaces})
@activity.defn
async def execute_agent_work_session(work_request: WorkRequest) -> WorkResult:
    """
    Modal handles:
    - Physical workspace access (/workspace/{startup_id}/)
    - Tool execution (MCP tools, file ops, git, etc.)
    - External API calls (OpenAI, GitHub, etc.)
    - Intensive compute work (code analysis, etc.)
    """

    # Modal has access to the workspace
    workspace_path = f"/workspace/{work_request.startup_id}"

    # Modal can use all your existing tools
    agent_tools = AgentToolkit(workspace_path)

    # Execute the work using existing infrastructure
    return await agent_tools.execute_work_session(work_request)
```

### **Responsibility Matrix**

| Capability | Temporal | Modal | Reason |
|------------|----------|-------|---------|
| **Agent Identity** | ✅ | ❌ | Persistent across months |
| **Long-term Memory** | ✅ | ❌ | Needs perfect state continuity |
| **Strategic Planning** | ✅ | ❌ | High-level orchestration |
| **Scheduling** | ✅ | ❌ | Built-in temporal scheduling |
| **Multi-agent Coordination** | ✅ | ❌ | Workflow orchestration |
| **File System Access** | ❌ | ✅ | Modal has workspace volumes |
| **OpenAI API Calls** | ❌ | ✅ | External API calls |
| **MCP Tool Execution** | ❌ | ✅ | Need workspace access |
| **GitHub Operations** | ❌ | ✅ | External API calls |
| **Code Analysis** | ❌ | ✅ | Compute-intensive work |
| **Real-time Responses** | ❌ | ✅ | Low-latency execution |

### **Clean Communication Pattern**

#### **Temporal -> Modal (Work Delegation)**
```python
# Temporal workflow delegates work to Modal
@workflow.defn
class CEOWorkflow:
    async def handle_user_message(self, message: str):
        # Temporal decides WHAT work needs to be done
        work_request = WorkRequest(
            startup_id=self.identity.startup_id,
            type="user_interaction",
            context={
                "message": message,
                "conversation_history": self.memory.recent_conversations(10),
                "current_goals": self.identity.long_term_goals,
                "agent_personality": self.identity.personality_traits
            }
        )

        # Modal executes the actual work
        result = await workflow.execute_activity(
            execute_user_interaction,
            work_request,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # Temporal updates long-term state
        self.memory.add_conversation("user", message)
        self.memory.add_conversation("ceo", result.response)
        self.memory.add_insights(result.insights)
```

#### **Modal -> Temporal (Work Results)**
```python
# Modal returns structured results to Temporal
@app.function(volumes={"/workspace": startup_workspaces})
@activity.defn
async def execute_user_interaction(work_request: WorkRequest) -> WorkResult:
    # Modal accesses workspace and executes tools
    workspace = AgentWorkspace(f"/workspace/{work_request.startup_id}")
    mcp_tools = MCPToolRegistry(workspace.path, work_request.startup_id)

    # Use existing CEO agent logic
    response = await process_user_message(
        message=work_request.context["message"],
        conversation_history=work_request.context["conversation_history"],
        tools=mcp_tools,
        workspace=workspace
    )

    # Return structured result
    return WorkResult(
        success=True,
        response=response.content,
        insights=response.insights,
        file_changes=response.file_changes,
        tool_executions=response.tool_executions
    )
```

### **Workspace Architecture**

#### **Modal Maintains Physical Workspace**
```
/workspace/{startup_id}/
├── current_work/              # Modal's active working directory
│   ├── github_repo/          # Cloned repo for current work
│   ├── temp_files/           # Temporary working files
│   └── analysis_cache/       # Cached analysis results
├── knowledge_base/            # Accumulated knowledge
│   ├── codebase_analysis/    # Deep code understanding
│   ├── user_patterns/        # User behavior insights
│   └── technical_decisions/  # Technical choice history
└── coordination/              # Inter-agent communication
    ├── shared_context/       # Context shared between agents
    └── work_handoffs/        # Work passed between agents
```

#### **Temporal Maintains Agent State**
```python
# Temporal keeps agent state in workflow variables (serializable)
class AgentMemory:
    conversations: List[Conversation]      # Full conversation history
    strategic_insights: List[Insight]     # High-level learnings
    personality_evolution: PersonalityState  # How agent changes over time
    relationship_context: Dict[str, Any]  # User relationship memory

class AgentIdentity:
    startup_id: str
    agent_type: str                       # CEO, Frontend Dev, etc.
    personality_traits: Dict[str, float]  # Creativity, caution, etc.
    specialization_areas: List[str]       # What this agent is good at
    coordination_preferences: Dict        # How agent likes to work with others
```

### **Updated Cost Structure**

#### **Temporal (Agent Consciousness)**
```
Development: $25/month for all agents
Production: $200/month for all agents
Actions: ~$5-20/month based on thinking frequency
```

#### **Modal (Agent Actions)**
```
Activities: $30-80/month per startup (only when working)
Storage: $1-5/month per startup (workspace volumes)
```

#### **Total Cost Comparison**
```
Current Functions:    $15/month per startup
Temporal + Modal:     $55-105/month total (all startups)
Modal Containers:     $720/month per startup
```

### **Benefits of Clean Separation**

1. **Temporal specializes** in long-term state and orchestration
2. **Modal specializes** in compute and workspace access
3. **Existing code mostly reusable** (just restructured as activities)
4. **Clean migration path** (can migrate one agent type at a time)
5. **Cost efficient** (pay for orchestration + compute separately)
6. **Best of both worlds** (reliability + performance)

**Key Principle: Don't make Temporal do Modal's job, and don't make Modal do Temporal's job.** Each platform handles what it's best at.

## 🛠️ Technical Migration Plan

### Phase 1: Foundation Setup (Week 1)

#### 1.1 Temporal Cloud Setup
```bash
# Create Temporal Cloud account
# Set up development namespace: my-yc-dev ($25/month)
# Configure authentication and certificates
```

#### 1.2 Local Development Environment
```bash
# Install Temporal SDK
pip install temporalio

# Create new project structure
mkdir temporal_agents/
├── workflows/
│   ├── ceo_workflow.py
│   └── startup_workflow.py
├── activities/
│   ├── mcp_activities.py
│   ├── openai_activities.py
│   └── github_activities.py
├── workers/
│   └── agent_worker.py
└── shared/
    └── data_models.py
```

#### 1.3 Data Models Design
```python
# shared/data_models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class CEOState:
    """Serializable state for CEO workflow"""
    startup_id: str
    conversation_history: List[Dict[str, str]]
    decisions: List[Dict[str, Any]]
    current_goals: List[str]
    last_activity: datetime
    status: str

@dataclass
class WorkRequest:
    """Input for work activities"""
    startup_id: str
    request_type: str
    content: str
    context: Dict[str, Any]

@dataclass
class WorkResult:
    """Output from work activities"""
    success: bool
    content: str
    updates: Dict[str, Any]
    next_actions: List[str]
```

### Phase 2: Core Workflow Implementation (Week 2)

#### 2.1 CEO Workflow
```python
# workflows/ceo_workflow.py
from temporalio import workflow
from datetime import timedelta
from shared.data_models import CEOState, WorkRequest

@workflow.defn
class CEOWorkflow:
    def __init__(self):
        self.state = CEOState(
            startup_id="",
            conversation_history=[],
            decisions=[],
            current_goals=[],
            last_activity=workflow.now(),
            status="initializing"
        )

    @workflow.run
    async def run(self, startup_id: str, design_doc: Dict[str, Any]) -> None:
        """Main CEO workflow - runs indefinitely for one startup"""
        self.state.startup_id = startup_id

        # Initialize the startup
        await self._initialize_startup(design_doc)

        # Main agent loop
        while True:
            # Wait for work or scheduled tasks
            await workflow.wait_condition(
                lambda: len(self._get_pending_work()) > 0,
                timeout=timedelta(hours=1)
            )

            # Process pending work
            pending_work = self._get_pending_work()
            for work in pending_work:
                await self._process_work_request(work)

            # Periodic reflection and planning
            if self._should_do_periodic_review():
                await self._periodic_review()

    async def _initialize_startup(self, design_doc: Dict[str, Any]):
        """Initialize startup through activities"""
        init_result = await workflow.execute_activity(
            initialize_startup_activity,
            args=[self.state.startup_id, design_doc],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3)
        )

        self.state.status = "ready"
        self._add_conversation("system", f"Startup initialized: {init_result}")

    @workflow.signal
    async def handle_user_message(self, message: str):
        """Handle incoming user messages"""
        self._add_conversation("user", message)

    @workflow.signal
    async def handle_scheduled_task(self, task_type: str):
        """Handle scheduled background tasks"""
        self._add_pending_work(task_type, {})

    async def _process_work_request(self, work: WorkRequest):
        """Process work through activities"""
        if work.request_type == "user_message":
            result = await workflow.execute_activity(
                handle_user_message_activity,
                args=[work],
                start_to_close_timeout=timedelta(minutes=5)
            )

            self._add_conversation("ceo", result.content)
            self._update_state(result.updates)

        elif work.request_type == "github_task":
            result = await workflow.execute_activity(
                handle_github_task_activity,
                args=[work],
                start_to_close_timeout=timedelta(minutes=10)
            )

            self._add_decision("github_action", work.content, result.content, "Automated GitHub task")

    def _add_conversation(self, role: str, content: str):
        """Add to conversation history (deterministic)"""
        self.state.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": workflow.now().isoformat()
        })

    # Helper methods for state management...
```

#### 2.2 Activity Implementation
```python
# activities/mcp_activities.py
from temporalio import activity
from shared.data_models import WorkRequest, WorkResult
import json

@activity.defn
async def handle_user_message_activity(work: WorkRequest) -> WorkResult:
    """Handle user messages using MCP tools"""

    # This is where all the current CEO logic goes
    # Import and use existing MCP tools
    from mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP

    # Initialize MCP tools (activity can do this)
    workspace_path = f"/workspace/{work.startup_id}"
    mcp_tools = MCPToolRegistry(workspace_path, work.startup_id)
    mcp_tools.register_tool("filesystem", FileSystemMCP)
    mcp_tools.register_tool("git", GitMCP)

    # Call OpenAI with tools (activity can do this)
    from openai import OpenAI
    openai = OpenAI()

    # Build conversation context
    messages = _build_messages(work.context["conversation_history"], work.content)
    tools = mcp_tools.get_all_openai_functions()

    # Get response from OpenAI
    response = await openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # Handle tool calls if any
    tool_results = []
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            result = await mcp_tools.execute_openai_function(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            tool_results.append(result)

    # Return result to workflow
    return WorkResult(
        success=True,
        content=response.choices[0].message.content,
        updates={"tool_results": tool_results},
        next_actions=[]
    )

@activity.defn
async def initialize_startup_activity(startup_id: str, design_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize startup workspace and GitHub repo"""

    # Use existing workspace manager
    from workspace_manager import WorkspaceManager
    from ceo_agent import CEOAgent

    workspace_mgr = WorkspaceManager()

    # Initialize workspace if needed
    if not workspace_mgr.workspace_exists(startup_id):
        workspace_path = workspace_mgr.initialize_workspace(
            startup_id,
            design_doc.get("title", f"Startup {startup_id}"),
            design_doc
        )

    # Create GitHub repo using existing CEO logic
    ceo = CEOAgent(startup_id, design_doc, workspace_mgr)
    result = await ceo.initialize_project()

    return result
```

### Phase 3: Worker Setup (Week 3)

#### 3.1 Worker Implementation
```python
# workers/agent_worker.py
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.ceo_workflow import CEOWorkflow
from activities import mcp_activities

async def main():
    """Run the agent worker"""
    # Connect to Temporal
    client = await Client.connect("my-yc-dev.tmprl.cloud:7233")

    # Create worker
    worker = Worker(
        client,
        task_queue="agent-task-queue",
        workflows=[CEOWorkflow],
        activities=[
            mcp_activities.handle_user_message_activity,
            mcp_activities.initialize_startup_activity,
            mcp_activities.handle_github_task_activity,
        ]
    )

    # Run worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 3.2 Workflow Starter
```python
# start_ceo.py
from temporalio.client import Client
from workflows.ceo_workflow import CEOWorkflow

async def start_ceo_for_startup(startup_id: str, design_doc: Dict[str, Any]):
    """Start a new CEO workflow for a startup"""
    client = await Client.connect("my-yc-dev.tmprl.cloud:7233")

    # Start workflow
    handle = await client.start_workflow(
        CEOWorkflow.run,
        args=[startup_id, design_doc],
        id=f"ceo-{startup_id}",
        task_queue="agent-task-queue"
    )

    return handle
```

### Phase 4: API Integration (Week 4)

#### 4.1 Update Frontend API Routes
```python
# Replace Modal calls with Temporal workflow signals
# frontend/app/api/ceo/chat/route.ts

export async function POST(req: NextRequest) {
    // Instead of calling Modal endpoint:
    // const ceoResponse = await fetch(MODAL_ENDPOINTS.CEO_CHAT, ...)

    // Call Temporal workflow signal:
    const temporalClient = await getTemporalClient()
    const handle = temporalClient.getHandle(f"ceo-{startup_id}")

    // Send message to workflow
    await handle.signal('handleUserMessage', message)

    // Get response (implement response mechanism)
    const response = await waitForResponse(handle, messageId)

    return streamResponse(response)
}
```

#### 4.2 Response Handling Pattern
```python
# Implement query pattern for getting responses
@workflow.query
def get_latest_response(self) -> Optional[str]:
    """Get the latest response from CEO"""
    if self.state.conversation_history:
        last_message = self.state.conversation_history[-1]
        if last_message["role"] == "ceo":
            return last_message["content"]
    return None
```

### Phase 5: Migration & Testing (Week 5)

#### 5.1 Parallel Deployment
```bash
# Deploy Temporal workers alongside existing Modal functions
# Route 10% of traffic to Temporal for testing
# Compare behavior and performance
```

#### 5.2 Data Migration
```python
# Migrate existing startup workspaces to Temporal workflows
# Start workflows for existing active startups
# Preserve conversation history and state
```

#### 5.3 Monitoring Setup
```python
# Set up Temporal UI monitoring
# Add custom metrics for agent performance
# Configure alerts for workflow failures
```

## 🎯 Success Metrics

### Technical Metrics
- **Workflow uptime**: >99% (compared to Modal function cold starts)
- **Response latency**: <500ms for conversation queries
- **State consistency**: 100% (no lost conversations or decisions)
- **Cost efficiency**: <$100/month per startup vs $720/month for Modal containers

### Agent Behavior Metrics
- **Context continuity**: Agents reference conversations from days/weeks ago
- **Autonomous initiative**: Agents take actions without user prompting
- **Long-term memory**: Agents build institutional knowledge over time
- **Multi-session coherence**: Conversations feel continuous across days

## 🚀 Go/No-Go Decision Framework

### Green Light Criteria ✅
- [ ] MVP validation shows product-market fit for autonomous agents
- [ ] Team has 40+ hours available for migration
- [ ] Monthly revenue >$500/startup (cost justification)
- [ ] Technical complexity acceptable for team skill level

### Red Light Criteria ❌
- [ ] Current "diary reading" approach meets user needs
- [ ] Team lacks capacity for 5-week migration project
- [ ] Monthly revenue <$100/startup (cost prohibitive)
- [ ] Platform dependency concerns outweigh benefits

## 📋 Implementation Checklist

### Week 1: Foundation
- [ ] Set up Temporal Cloud development namespace
- [ ] Install Temporal SDK and dev environment
- [ ] Design data models and workflow architecture
- [ ] Create basic project structure

### Week 2: Core Implementation
- [ ] Implement CEOWorkflow with basic state management
- [ ] Create core activities for user messages and GitHub tasks
- [ ] Test workflow execution with simple scenarios
- [ ] Implement workflow signals and queries

### Week 3: Integration
- [ ] Build and deploy worker process
- [ ] Integrate existing MCP tools into activities
- [ ] Test end-to-end workflow execution
- [ ] Implement proper error handling and retries

### Week 4: API Updates
- [ ] Update frontend routes to call Temporal instead of Modal
- [ ] Implement response streaming from workflows
- [ ] Add workflow monitoring and health checks
- [ ] Test integration with existing frontend

### Week 5: Migration
- [ ] Deploy workers to production
- [ ] Migrate existing startup data to workflows
- [ ] Implement traffic routing and A/B testing
- [ ] Monitor performance and fix issues

## 🎉 Expected Outcomes

### Immediate Benefits (Month 1)
- **Cost reduction**: 2-11x cheaper than Modal containers for persistent agents
- **True persistence**: Agents maintain consciousness across all interactions
- **Faster responses**: No cold start delays, instant context retrieval

### Long-term Benefits (Months 2-6)
- **Autonomous behavior**: Agents take initiative and work independently
- **Institutional memory**: Agents build deep knowledge of each startup
- **Scalable architecture**: Can handle hundreds of concurrent agent workflows
- **Enterprise features**: Built-in monitoring, fault tolerance, and audit trails

This migration represents a fundamental shift from "AI tools that humans use" to "AI entities that operate autonomously" - the core vision of truly persistent, long-term autonomous agents.