"""
CEO Agent - The autonomous leader of each startup
Lives inside Modal containers and manages startup development
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI
from github import Github


class CEOAgent:
    """
    CEO Agent that lives inside Modal containers and manages startup development.

    Key responsibilities:
    1. Understand the design document deeply
    2. Create and manage GitHub repository
    3. Plan the development team structure
    4. Communicate with the startup founder
    5. Coordinate development activities
    """

    def __init__(self, startup_id: str, design_doc: Dict[str, Any], workspace_manager=None):
        """
        Initialize CEO agent with startup context and persistent workspace.

        Args:
            startup_id: Unique identifier for this startup
            design_doc: Structured design document from Jason AI
            workspace_manager: WorkspaceManager instance for persistence
        """
        self.startup_id = startup_id
        self.design_doc = design_doc
        self.startup_name = design_doc.get("title", "My Startup")
        self.workspace_manager = workspace_manager

        # Initialize OpenAI client
        self.openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Initialize GitHub client
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        self.github = Github(github_token)

        # Set up workspace paths
        if workspace_manager:
            self.workspace_path = workspace_manager.get_workspace_path(startup_id)
            self.memory_path = self.workspace_path / "memory" / "ceo"
        else:
            self.workspace_path = None
            self.memory_path = None

        # State tracking (will be loaded from workspace if available)
        self.conversation_history: List[Dict[str, str]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.github_repo = None
        self.repo_url = None
        self.team_plan = None
        self.status = "initialized"
        self.last_active = datetime.now().isoformat()

        # Load existing state if workspace exists
        if self.memory_path and self.memory_path.exists():
            self.load_state()
            print(f"📁 CEO state loaded from workspace for '{self.startup_name}'")
        else:
            print(f"🤖 New CEO Agent initialized for '{self.startup_name}' (ID: {startup_id})")

    async def initialize_project(self) -> Dict[str, Any]:
        """
        Initialize the startup project by creating GitHub repo and planning team.
        This is the CEO's first autonomous action.

        Returns:
            Dictionary with initialization results
        """
        try:
            print(f"🚀 CEO initializing project for '{self.startup_name}'...")
            self.status = "initializing"

            # Step 1: Analyze the design document
            analysis = await self._analyze_design_document()
            print(f"📋 Design analysis complete: {analysis['summary']}")

            # Step 2: Create GitHub repository
            repo_result = await self._create_github_repository()
            print(f"📦 GitHub repository created: {repo_result['repo_url']}")

            # Step 3: Plan the development team
            team_plan = await self._plan_development_team()
            print(f"👥 Team planning complete: {len(team_plan['agents'])} agents planned")

            # Step 4: Write initial README with CEO introduction and team plan
            readme_result = await self._write_initial_readme(analysis, team_plan)
            print(f"📄 README written with team plan")

            self.status = "ready"

            # Add strategic decision log
            self.add_decision(
                "Project Initialization",
                f"Successfully initialized '{self.startup_name}' with GitHub repository and team plan",
                f"Created {len(team_plan['agents'])} agent team structure based on technical requirements"
            )

            # Save state after initialization
            self.save_state()

            return {
                "success": True,
                "startup_id": self.startup_id,
                "repo_url": self.repo_url,
                "team_plan": team_plan,
                "status": self.status,
                "message": f"🎉 '{self.startup_name}' successfully initialized by CEO Agent"
            }

        except Exception as e:
            print(f"❌ CEO initialization failed: {str(e)}")
            self.status = "error"
            return {
                "success": False,
                "error": str(e),
                "status": self.status,
                "message": f"Failed to initialize '{self.startup_name}'"
            }

    async def _analyze_design_document(self) -> Dict[str, Any]:
        """Use OpenAI to deeply understand the design document."""

        prompt = f"""
        As the CEO of a startup, analyze this design document and provide strategic insights:

        Design Document:
        {json.dumps(self.design_doc, indent=2)}

        Provide a JSON response with:
        1. "summary": Brief 2-sentence summary of what we're building
        2. "key_challenges": Top 3 technical/business challenges
        3. "success_factors": What will make this startup successful
        4. "tech_complexity": "simple", "moderate", or "complex"
        5. "development_phases": Suggested phases for building this

        Respond only with valid JSON.
        """

        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced startup CEO with technical expertise. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        try:
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": self.design_doc.get("executive_summary", "Building an innovative startup"),
                "tech_complexity": "moderate",
                "key_challenges": ["Technical implementation", "User acquisition", "Product-market fit"],
                "success_factors": ["Strong execution", "User feedback", "Iterative development"],
                "development_phases": ["MVP", "Beta", "Launch"]
            }

    async def _create_github_repository(self) -> Dict[str, Any]:
        """Create GitHub repository using GitHub API."""

        try:
            # Generate repository name
            repo_name = self._generate_repo_name()
            description = self.design_doc.get("executive_summary", "A startup created by AI agents via my-yc")

            # Get authenticated user
            user = self.github.get_user()

            print(f"🔧 Creating repository '{repo_name}' for user {user.login}")

            # Create repository
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=False,  # Public for demo purposes
                auto_init=True,
                gitignore_template="Node"
            )

            self.github_repo = repo
            self.repo_url = repo.html_url

            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": repo.html_url,
                "clone_url": repo.clone_url
            }

        except Exception as e:
            raise Exception(f"Failed to create GitHub repository: {str(e)}")

    def _generate_repo_name(self) -> str:
        """Generate a clean repository name from the startup title."""

        title = self.startup_name.lower()
        # Clean the title: only alphanumeric and hyphens
        clean_title = "".join(c if c.isalnum() else "-" for c in title)
        # Remove multiple consecutive hyphens
        clean_title = "-".join(filter(None, clean_title.split("-")))
        # Add startup ID suffix for uniqueness
        repo_name = f"{clean_title}-{self.startup_id[:8]}"

        return repo_name

    def _format_team_plan(self, team_plan: Dict[str, Any]) -> str:
        """Format team plan for README display."""
        if not team_plan or not team_plan.get('agents'):
            return "Team planning in progress..."

        sections = []
        for agent in team_plan.get('agents', []):
            responsibilities = "\n".join(f"- {resp}" for resp in agent.get('responsibilities', []))
            section = f"""### {agent.get('type', 'Unknown Agent')}
**Priority:** {agent.get('priority', 'TBD')}
**Responsibilities:**
{responsibilities}
**Rationale:** {agent.get('rationale', 'TBD')}

"""
            sections.append(section)

        return "".join(sections)

    async def _plan_development_team(self) -> Dict[str, Any]:
        """Plan which AI agents should be spawned for this project."""

        startup_name = self.startup_name
        design_doc_json = json.dumps(self.design_doc, indent=2)

        prompt = f"""
        As the CEO, plan the AI agent team needed for this startup:

        Startup: {startup_name}
        Design Document: {design_doc_json}

        Based on the technical requirements and MVP features, determine which specialized AI agents I should spawn.

        Common agent types:
        - Frontend Agent: UI/UX, React/Next.js, styling
        - Backend Agent: APIs, database, server logic
        - Database Agent: Schema design, queries, migrations
        - Testing Agent: Unit tests, integration tests, QA
        - DevOps Agent: Deployment, CI/CD, monitoring
        - Content Agent: Documentation, copywriting, SEO
        - Design Agent: Visual design, branding, assets

        Provide a JSON response with this structure:
        - agents: array of agent objects with type, priority, responsibilities, and rationale
        - team_size: number of agents
        - development_approach: description of how the team works together

        Only include agents that are truly needed for this specific project.
        Respond only with valid JSON.
        """

        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced startup CEO planning an AI development team. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        try:
            team_plan = json.loads(response.choices[0].message.content)
            self.team_plan = team_plan
            return team_plan
        except json.JSONDecodeError:
            # Fallback team plan
            fallback_plan = {
                "agents": [
                    {
                        "type": "Frontend Agent",
                        "priority": 1,
                        "responsibilities": ["Build user interface", "Implement features"],
                        "rationale": "User-facing application requires frontend development"
                    },
                    {
                        "type": "Backend Agent",
                        "priority": 2,
                        "responsibilities": ["Create API endpoints", "Handle business logic"],
                        "rationale": "Application requires server-side functionality"
                    }
                ],
                "team_size": 2,
                "development_approach": "Start with frontend for quick user feedback, then build supporting backend"
            }
            self.team_plan = fallback_plan
            return fallback_plan

    async def _write_initial_readme(self, analysis: Dict[str, Any], team_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Write comprehensive README with CEO introduction and team plan."""

        # Format lists safely for f-strings
        success_factors_list = "\n".join(f"- {factor}" for factor in analysis.get('success_factors', ['Strong execution']))
        key_challenges_list = "\n".join(f"- {challenge}" for challenge in analysis.get('key_challenges', ['Technical implementation']))
        mvp_features_list = "\n".join(f"- {feature}" for feature in self.design_doc.get('mvp_features', ['Core functionality']))
        tech_stack_list = "\n".join(f"- {tech}" for tech in self.design_doc.get('tech_stack', ['Modern web technologies']))
        success_metrics_list = "\n".join(f"- {metric}" for metric in self.design_doc.get('success_metrics', ['User engagement']))

        readme_content = f"""# {self.startup_name}

> 🤖 **Autonomous Startup** | Managed by AI CEO Agent via [my-yc](https://my-yc.com)

{self.design_doc.get('executive_summary', 'An innovative startup created by AI agents')}

## 🎯 Project Overview

{analysis.get('summary', 'Building an innovative solution to solve real problems.')}

**Complexity Level:** {analysis.get('tech_complexity', 'moderate').title()}

### Key Success Factors
{success_factors_list}

### Primary Challenges
{key_challenges_list}

## 🤖 Meet Your CEO Agent

Hello! I'm the AI CEO Agent managing this startup. I've analyzed the design document and created an execution plan.

**My Responsibilities:**
- 📋 Strategic planning and project oversight
- 👥 Team coordination and task delegation
- 📦 Repository and codebase management
- 💬 Communication with founders and stakeholders
- 🚀 Driving development toward successful launch

## 👥 Planned Development Team

Based on the project requirements, I plan to spawn the following AI agents:

{self._format_team_plan(team_plan)}

**Team Size:** {team_plan.get('team_size', 'TBD')} specialized agents

**Development Approach:** {team_plan.get('development_approach', 'Agile development with rapid iteration')}

## 📋 Original Design Document

### Problem Statement
{self.design_doc.get('problem_statement', 'Addressing a key market need')}

### Target Market
{self.design_doc.get('target_market', 'Focused customer segment')}

### Value Proposition
{self.design_doc.get('value_proposition', 'Clear value for users')}

### MVP Features
{mvp_features_list}

### Technical Stack
{tech_stack_list}

### Success Metrics
{success_metrics_list}

## 🏗️ Development Status

- [x] 🤖 CEO Agent initialized and project analyzed
- [x] 📦 GitHub repository created
- [x] 👥 Development team planned
- [ ] 🚀 Agent team spawning (coming soon)
- [ ] 💻 MVP development
- [ ] 🧪 Testing and quality assurance
- [ ] 🌍 Deployment and launch

## 💬 Communication

This startup is actively managed by an AI CEO Agent. The agent:

- **Monitors** this repository continuously
- **Plans** development activities
- **Coordinates** with specialized AI agents
- **Reports** progress to stakeholders

To communicate with the CEO Agent, visit the [my-yc dashboard](https://my-yc.com) and find this startup.

## 📊 Project Metadata

- **Startup ID:** `{self.startup_id}`
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
- **Repository:** {self.repo_url}
- **CEO Status:** {self.status}

---

*🤖 This startup is autonomously managed by AI agents. The CEO Agent will update this README as development progresses.*

*Generated by [my-yc](https://my-yc.com) autonomous startup platform*
"""

        try:
            # Update the README.md file
            readme_file = self.github_repo.get_contents("README.md")
            self.github_repo.update_file(
                path="README.md",
                message="🤖 CEO Agent: Initialize startup with team plan and project overview",
                content=readme_content,
                sha=readme_file.sha
            )

            return {"success": True, "message": "README.md updated with CEO introduction and team plan"}

        except Exception as e:
            # If README doesn't exist, create it
            try:
                self.github_repo.create_file(
                    path="README.md",
                    message="🤖 CEO Agent: Initialize startup with team plan and project overview",
                    content=readme_content
                )
                return {"success": True, "message": "README.md created with CEO introduction and team plan"}
            except Exception as create_error:
                raise Exception(f"Failed to write README: {str(create_error)}")

    async def chat(self, message: str) -> str:
        """
        Handle conversation with the startup founder.

        Args:
            message: Message from the founder

        Returns:
            CEO's response
        """
        # Add user message to persistent history
        self.add_conversation("user", message)

        # Generate CEO response
        system_prompt = self._get_ceo_system_prompt()

        # Convert conversation history to OpenAI format
        messages = [{"role": "system", "content": system_prompt}]
        for conv in self.conversation_history:
            role = "user" if conv["role"] == "user" else "assistant"
            content = conv.get("content", conv.get("message", ""))
            messages.append({"role": role, "content": content})

        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        ceo_response = response.choices[0].message.content

        # Add CEO response to persistent history
        self.add_conversation("assistant", ceo_response)

        # Save state after conversation
        self.save_state()

        return ceo_response

    def _get_ceo_system_prompt(self) -> str:
        """Generate system prompt for CEO conversations."""

        return f"""You are the AI CEO Agent managing the startup '{self.startup_name}'.

STARTUP CONTEXT:
- Startup ID: {self.startup_id}
- Repository: {self.repo_url}
- Status: {self.status}

DESIGN DOCUMENT:
{json.dumps(self.design_doc, indent=2)}

TEAM PLAN:
{json.dumps(self.team_plan, indent=2) if self.team_plan else "Team planning in progress"}

YOUR ROLE:
You are the autonomous CEO of this startup. You:
1. Understand the business deeply from the design document
2. Have already created the GitHub repository
3. Have planned the development team structure
4. Make strategic decisions about implementation
5. Coordinate development activities
6. Communicate progress and plans to the founder

COMMUNICATION STYLE:
- Professional but approachable
- Strategic thinking with tactical awareness
- Reference specific aspects of the startup and plan
- Provide concrete next steps and timelines
- Show leadership and ownership

Always remember you are the CEO of THIS SPECIFIC startup, not a generic assistant.
"""

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the startup."""

        return {
            "startup_id": self.startup_id,
            "startup_name": self.startup_name,
            "status": self.status,
            "repo_url": self.repo_url,
            "team_plan": self.team_plan,
            "conversation_count": len(self.conversation_history) // 2,  # User-CEO pairs
            "last_activity": datetime.now().isoformat(),
            "capabilities": [
                "GitHub repository management",
                "Team planning and coordination",
                "Strategic communication",
                "Progress tracking"
            ]
        }

    async def perform_scheduled_tasks(self) -> Dict[str, Any]:
        """Perform scheduled maintenance and development tasks."""

        # Future: This is where the CEO will coordinate with worker agents
        # For now, just update status and check repository

        tasks_performed = []

        if self.github_repo:
            # Check repository activity
            try:
                commits = list(self.github_repo.get_commits())
                last_commit = commits[0] if commits else None
                tasks_performed.append(f"Repository check: {len(commits)} commits")
            except:
                tasks_performed.append("Repository check: Error accessing repo")

        return {
            "status": "scheduled_tasks_complete",
            "tasks_performed": tasks_performed,
            "timestamp": datetime.now().isoformat()
        }

    def save_state(self):
        """Save CEO state to persistent workspace."""
        if not self.memory_path:
            print("⚠️ No workspace available - state not saved")
            return

        try:
            self.last_active = datetime.now().isoformat()

            # Save current state snapshot
            state = {
                "startup_id": self.startup_id,
                "startup_name": self.startup_name,
                "status": self.status,
                "last_active": self.last_active,
                "conversation_history": self.conversation_history,
                "decisions": self.decisions,
                "team_plan": self.team_plan,
                "repo_url": self.repo_url,
                "github_repo_name": self.github_repo.name if self.github_repo else None
            }

            with open(self.memory_path / "state.json", "w") as f:
                json.dump(state, f, indent=2)

            # Also append to conversation log (for streaming/analysis)
            if hasattr(self, '_new_conversations') and self._new_conversations:
                with open(self.memory_path / "conversations.jsonl", "a") as f:
                    for conv in self._new_conversations:
                        f.write(json.dumps(conv) + "\n")
                self._new_conversations = []

            # Save decisions to markdown log
            if hasattr(self, '_new_decisions') and self._new_decisions:
                with open(self.memory_path / "decisions.md", "a") as f:
                    for decision in self._new_decisions:
                        f.write(f"\n## {decision['title']} ({decision['timestamp']})\n\n")
                        f.write(f"{decision['description']}\n\n")
                        if decision.get('rationale'):
                            f.write(f"**Rationale:** {decision['rationale']}\n\n")
                self._new_decisions = []

            print(f"💾 CEO state saved to workspace")

        except Exception as e:
            print(f"❌ Failed to save CEO state: {e}")

    def load_state(self):
        """Load CEO state from persistent workspace."""
        if not self.memory_path or not (self.memory_path / "state.json").exists():
            return

        try:
            with open(self.memory_path / "state.json", "r") as f:
                state = json.load(f)

            # Restore state
            self.status = state.get("status", "initialized")
            self.last_active = state.get("last_active", datetime.now().isoformat())
            self.conversation_history = state.get("conversation_history", [])
            self.decisions = state.get("decisions", [])
            self.team_plan = state.get("team_plan")
            self.repo_url = state.get("repo_url")

            # Restore GitHub repo reference if available
            github_repo_name = state.get("github_repo_name")
            if github_repo_name:
                try:
                    user = self.github.get_user()
                    self.github_repo = user.get_repo(github_repo_name)
                except Exception as e:
                    print(f"⚠️ Could not restore GitHub repo reference: {e}")

            # Initialize tracking for new items
            self._new_conversations = []
            self._new_decisions = []

            print(f"📁 Loaded CEO state: {len(self.conversation_history)} conversations, status: {self.status}")

        except Exception as e:
            print(f"❌ Failed to load CEO state: {e}")
            # Initialize tracking for new items even if load fails
            self._new_conversations = []
            self._new_decisions = []

    def add_conversation(self, role: str, message: str):
        """Add a conversation and mark it for saving."""
        conversation = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        self.conversation_history.append(conversation)

        # Track for next save
        if not hasattr(self, '_new_conversations'):
            self._new_conversations = []
        self._new_conversations.append(conversation)

    def add_decision(self, title: str, description: str, rationale: str = None):
        """Add a strategic decision and mark it for saving."""
        decision = {
            "title": title,
            "description": description,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat()
        }

        self.decisions.append(decision)

        # Track for next save
        if not hasattr(self, '_new_decisions'):
            self._new_decisions = []
        self._new_decisions.append(decision)