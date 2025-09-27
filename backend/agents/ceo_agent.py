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

        # Initialize MCP tools for workspace operations
        self.mcp_tools = None
        if self.workspace_path:
            try:
                # Try absolute import first (for Modal containers)
                import sys
                sys.path.insert(0, "/root")
                from mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP
            except ImportError:
                # Fallback to relative import (for local testing)
                from .mcp_tools import MCPToolRegistry, FileSystemMCP, GitMCP, DocumentationMCP, GitHubCoordinationMCP

            self.mcp_tools = MCPToolRegistry(self.workspace_path, startup_id)
            self.mcp_tools.register_tool("filesystem", FileSystemMCP)
            self.mcp_tools.register_tool("git", GitMCP)
            self.mcp_tools.register_tool("documentation", DocumentationMCP)
            self.mcp_tools.register_tool("github", GitHubCoordinationMCP, github_token=github_token)

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

    async def handle_work_request(self, request: str) -> str:
        """
        Handle work requests from founders using OpenAI function calling.
        The LLM autonomously decides which MCP tools to use and when.
        """
        if not self.mcp_tools:
            return "I need a workspace to handle work requests. Please initialize the CEO first."

        # Add user request to conversation history
        self.add_conversation("user", request)

        try:
            # Use OpenAI function calling for autonomous tool usage
            response = await self._chat_with_tools(request)

            # Add CEO response to conversation history
            self.add_conversation("ceo", response)

            # Save state after handling request
            self.save_state()

            return response

        except Exception as e:
            error_msg = f"I encountered an issue while handling your request: {str(e)}"
            self.add_conversation("ceo", error_msg)
            self.save_state()
            return error_msg

    async def _chat_with_tools(self, request: str) -> str:
        """
        Chat with OpenAI using function calling for autonomous tool usage.
        """
        # Define available MCP tools as OpenAI functions
        tools = [
            # Filesystem Tools
            {
                "type": "function",
                "function": {
                    "name": "get_project_overview",
                    "description": "Get overview of the project including repository status, file count, and workspace info",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_project_structure",
                    "description": "Analyze the project's file structure and architecture",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a specific file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to read"},
                            "max_lines": {"type": "integer", "description": "Maximum lines to read (optional)"}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file (creates or overwrites)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file to write"},
                            "content": {"type": "string", "description": "Content to write to the file"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and folders in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dir_path": {"type": "string", "description": "Directory path to list (default: current)"},
                            "show_hidden": {"type": "boolean", "description": "Include hidden files"}
                        }
                    }
                }
            },

            # Git Tools
            {
                "type": "function",
                "function": {
                    "name": "get_git_status",
                    "description": "Get current git repository status including uncommitted changes",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recent_git_changes",
                    "description": "Get recent git commits and activity",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "since_hours": {"type": "integer", "description": "Hours to look back (default 72)"}
                        }
                    }
                }
            },

            # Documentation Tools
            {
                "type": "function",
                "function": {
                    "name": "get_project_documentation_status",
                    "description": "Get status of project documentation and TODO lists",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_specification",
                    "description": "Create or update project specification documents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spec_type": {"type": "string", "description": "Type of specification (feature, api, architecture)"},
                            "title": {"type": "string", "description": "Specification title"},
                            "content": {"type": "string", "description": "Specification content"}
                        },
                        "required": ["spec_type", "title", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_todo_item",
                    "description": "Add item to project TODO list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string", "description": "TODO item description"},
                            "priority": {"type": "string", "description": "Priority level (low, medium, high)"}
                        },
                        "required": ["item"]
                    }
                }
            },

            # GitHub Tools
            {
                "type": "function",
                "function": {
                    "name": "create_github_issue",
                    "description": "Create a new GitHub issue",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Issue title"},
                            "body": {"type": "string", "description": "Issue description"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "Issue labels"}
                        },
                        "required": ["title", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_github_issues",
                    "description": "List GitHub issues",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "state": {"type": "string", "description": "Issue state (open, closed, all)"},
                            "limit": {"type": "integer", "description": "Maximum number of issues to return"}
                        }
                    }
                }
            }
        ]

        # Create conversation context
        messages = [
            {
                "role": "system",
                "content": f"""You are the CEO of {self.startup_name}, an AI-managed startup.

Your role:
- Strategic oversight and coordination
- Understanding project status and progress
- Making high-level decisions about features and direction
- Managing all aspects of the project including files, documentation, and GitHub

Your capabilities:
- You CAN read, write, and modify any project files
- You CAN create documentation, specifications, and TODO items
- You CAN manage GitHub issues and milestones
- You CAN analyze code structure and git history
- You ARE the decision-maker and executor, not just an advisor

Your personality:
- Professional but approachable
- Strategic thinker
- Action-oriented - you get things done
- Transparent about what you're doing when you use tools
- Focused on business value and user needs

Use the available tools to both gather information AND take action as needed. You're not limited to just providing advice - you can and should execute tasks directly.

Current startup context:
- Startup: {self.startup_name}
- Status: {self.status}
- Repository: {'Available' if self.repo_url else 'Not set up yet'}"""
            },
            {
                "role": "user",
                "content": request
            }
        ]

        # Use OpenAI function calling
        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )

        # Handle function calls
        message = response.choices[0].message

        if message.tool_calls:
            # Add the assistant's message with tool calls
            messages.append(message)

            # Execute each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the corresponding MCP tool
                result = await self._execute_function_call(function_name, function_args)

                # Add the function result to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })

            # Get final response from OpenAI
            final_response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )

            return final_response.choices[0].message.content
        else:
            return message.content

    async def _execute_function_call(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool based on function call."""
        try:
            # Filesystem Tools
            if function_name == "get_project_overview":
                return await self.mcp_tools.execute_tool("filesystem", "get_project_overview")

            elif function_name == "analyze_project_structure":
                return await self.mcp_tools.execute_tool("filesystem", "analyze_project_structure")

            elif function_name == "read_file":
                file_path = args.get("file_path")
                max_lines = args.get("max_lines")
                kwargs = {"file_path": file_path}
                if max_lines:
                    kwargs["max_lines"] = max_lines
                return await self.mcp_tools.execute_tool("filesystem", "read_file", **kwargs)

            elif function_name == "write_file":
                file_path = args.get("file_path")
                content = args.get("content")
                return await self.mcp_tools.execute_tool("filesystem", "write_file", file_path=file_path, content=content)

            elif function_name == "list_directory":
                dir_path = args.get("dir_path", ".")
                show_hidden = args.get("show_hidden", False)
                return await self.mcp_tools.execute_tool("filesystem", "list_directory", dir_path=dir_path, show_hidden=show_hidden)

            # Git Tools
            elif function_name == "get_git_status":
                return await self.mcp_tools.execute_tool("git", "get_status")

            elif function_name == "get_recent_git_changes":
                since_hours = args.get("since_hours", 72)
                return await self.mcp_tools.execute_tool("git", "get_recent_changes", since_hours=since_hours)

            # Documentation Tools
            elif function_name == "get_project_documentation_status":
                return await self.mcp_tools.execute_tool("documentation", "get_project_status")

            elif function_name == "create_specification":
                spec_type = args.get("spec_type")
                title = args.get("title")
                content = args.get("content")
                return await self.mcp_tools.execute_tool("documentation", "create_specification",
                                                       spec_type=spec_type, title=title, content=content)

            elif function_name == "add_todo_item":
                item = args.get("item")
                priority = args.get("priority", "medium")
                return await self.mcp_tools.execute_tool("documentation", "add_todo_item",
                                                       item=item, priority=priority)

            # GitHub Tools
            elif function_name == "create_github_issue":
                title = args.get("title")
                body = args.get("body")
                labels = args.get("labels", [])
                return await self.mcp_tools.execute_tool("github", "create_issue",
                                                       title=title, body=body, labels=labels)

            elif function_name == "list_github_issues":
                state = args.get("state", "open")
                limit = args.get("limit", 10)
                return await self.mcp_tools.execute_tool("github", "list_issues",
                                                       state=state, limit=limit)

            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _analyze_work_request(self, request: str) -> Dict[str, Any]:
        """Analyze work request to determine required actions."""
        # Use OpenAI to understand the request
        prompt = f"""
        As a CEO Agent with access to development tools, analyze this work request:

        Request: "{request}"

        Context:
        - Startup: {self.startup_name}
        - Current Status: {self.status}
        - Has Repository: {"Yes" if self.repo_url else "No"}

        Available tools:
        - filesystem: Read/write files, understand codebase
        - git: Check history, commit changes, repository health
        - documentation: Create specs, manage TODO lists, document decisions
        - github: Create issues, manage milestones, coordinate tasks

        Respond with JSON containing:
        {{
            "request_type": "status_inquiry|feature_request|bug_fix|documentation|coordination",
            "priority": "low|medium|high|urgent",
            "required_tools": ["tool1", "tool2"],
            "action_plan": ["step1", "step2", "step3"],
            "estimated_complexity": "simple|moderate|complex"
        }}

        Focus on strategic oversight, not detailed implementation.
        """

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic CEO agent. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            # Fallback analysis
            return {
                "request_type": "general_inquiry",
                "priority": "medium",
                "required_tools": ["documentation"],
                "action_plan": ["Acknowledge request", "Provide status update"],
                "estimated_complexity": "simple"
            }

    async def _execute_work_plan(self, analysis: Dict[str, Any], original_request: str) -> str:
        """Execute work plan autonomously using available MCP tools."""
        required_tools = analysis.get("required_tools", [])
        action_plan = analysis.get("action_plan", [])

        # Let the CEO autonomously decide how to use tools and respond
        tool_execution_prompt = f"""
        As the CEO of {self.startup_name}, respond naturally to this request: "{original_request}"

        Your analysis determined you need these tools: {required_tools}
        Your action plan: {action_plan}

        Available MCP tools and their capabilities:
        - filesystem: get_project_overview, analyze_project_structure, read_file, write_file, list_directory
        - git: get_status, get_recent_changes, get_commit_history
        - documentation: get_project_status, get_todo_list, create_specification
        - github: create_issue, list_issues, create_milestone

        Respond conversationally while transparently using tools. Format tool usage as:
        "Let me check... *using filesystem: get_project_overview* I can see that..."

        Be natural, strategic, and helpful. Use tools as needed to gather information and take action.
        """

        try:
            # Get tool execution instructions from LLM
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic CEO agent. Be conversational and transparent about tool usage. Respond naturally while indicating what tools you're using."},
                    {"role": "user", "content": tool_execution_prompt}
                ],
                temperature=0.7
            )

            ceo_response = response.choices[0].message.content

            # Execute actual tool calls based on the response
            final_response = await self._execute_tools_from_response(ceo_response, required_tools)

            return final_response

        except Exception as e:
            return f"I encountered an issue while processing your request: {str(e)}. Let me gather some basic project information for you instead."

    async def _execute_tools_from_response(self, ceo_response: str, required_tools: List[str]) -> str:
        """
        Parse CEO response and execute actual tool calls, replacing placeholders with real data.
        """
        import re

        final_response = ceo_response

        # Find tool usage patterns like "*using filesystem: get_project_overview*"
        tool_pattern = r'\*using (\w+): ([^*]+)\*'
        tool_matches = re.findall(tool_pattern, ceo_response, re.IGNORECASE)

        for tool_name, action in tool_matches:
            if tool_name in self.mcp_tools.tools:
                try:
                    # Execute the tool
                    result = await self.mcp_tools.execute_tool(tool_name, action.strip())

                    if result["success"]:
                        # Replace the placeholder with actual results
                        placeholder = f"*using {tool_name}: {action}*"

                        # Format the result based on tool type
                        if tool_name == "filesystem" and action.strip() == "get_project_overview":
                            overview = result["result"]
                            replacement = f"*using {tool_name}: {action}* {self._format_project_overview(overview)}"
                        elif tool_name == "git" and "status" in action:
                            git_info = result["result"]
                            replacement = f"*using {tool_name}: {action}* {self._format_git_status(git_info)}"
                        else:
                            # Generic formatting
                            replacement = f"*using {tool_name}: {action}* ✅"

                        final_response = final_response.replace(placeholder, replacement)
                    else:
                        # Replace with error message
                        placeholder = f"*using {tool_name}: {action}*"
                        replacement = f"*using {tool_name}: {action}* ❌ {result.get('error', 'Failed')}"
                        final_response = final_response.replace(placeholder, replacement)

                except Exception as e:
                    # Replace with error
                    placeholder = f"*using {tool_name}: {action}*"
                    replacement = f"*using {tool_name}: {action}* ❌ Error: {str(e)}"
                    final_response = final_response.replace(placeholder, replacement)

        return final_response

    def _format_project_overview(self, overview: Dict[str, Any]) -> str:
        """Format project overview for natural conversation."""
        parts = []
        if overview.get("github_repo_status") == "present":
            parts.append("the GitHub repository is active")
        if overview.get("total_files"):
            parts.append(f"we have {overview['total_files']} files in the project")

        return "I can see " + (", ".join(parts) if parts else "the project workspace is set up")

    def _format_git_status(self, git_info: Dict[str, Any]) -> str:
        """Format git status for natural conversation."""
        if git_info.get("clean"):
            return "the repository is clean with no pending changes"
        else:
            changes = git_info.get("total_changes", 0)
            return f"there are {changes} uncommitted changes in the repository"

    async def _handle_status_inquiry(self) -> str:
        """Handle status inquiries using MCP tools."""
        try:
            status_parts = []

            # Always start with basic startup info
            status_parts.append(f"📊 **Project Overview for {self.startup_name}**")

            # Get project overview
            if "filesystem" in self.mcp_tools.tools:
                try:
                    overview_result = await self.mcp_tools.execute_tool("filesystem", "get_project_overview")
                    if overview_result["success"]:
                        overview = overview_result["result"]

                        if overview.get("github_repo_status") == "present":
                            status_parts.append("✅ GitHub repository is active and cloned in workspace")

                            # Get git status if repo is present
                            if "git" in self.mcp_tools.tools:
                                try:
                                    git_status_result = await self.mcp_tools.execute_tool("git", "get_status")
                                    if git_status_result["success"]:
                                        git_status = git_status_result["result"]
                                        if git_status.get("clean"):
                                            status_parts.append("✅ Repository is clean (no uncommitted changes)")
                                        else:
                                            changes = git_status.get("total_changes", 0)
                                            status_parts.append(f"📝 {changes} uncommitted changes in repository")

                                    # Get recent activity
                                    recent_result = await self.mcp_tools.execute_tool("git", "get_recent_changes", since_hours=72)
                                    if recent_result["success"]:
                                        recent = recent_result["result"]
                                        if recent.get("has_activity"):
                                            activity_count = recent.get("total_changes", 0)
                                            status_parts.append(f"🔄 {activity_count} commits in the last 3 days")
                                        else:
                                            status_parts.append("⏸️ No recent development activity")
                                except Exception as git_error:
                                    status_parts.append(f"⚠️ Git tools error: {str(git_error)}")
                        else:
                            status_parts.append("⚠️ GitHub repository not yet cloned to workspace")
                            status_parts.append("📋 CEO workspace is ready for development coordination")
                    else:
                        status_parts.append(f"⚠️ Filesystem tools error: {overview_result.get('error', 'Unknown error')}")
                except Exception as fs_error:
                    status_parts.append(f"⚠️ Filesystem tools unavailable: {str(fs_error)}")
            else:
                status_parts.append("⚠️ Filesystem tools not available")

            # Get current project status from documentation
            if "documentation" in self.mcp_tools.tools:
                project_status_result = await self.mcp_tools.execute_tool("documentation", "get_project_status")
                if project_status_result["success"]:
                    proj_status = project_status_result["result"]
                    if proj_status.get("status") != "unknown":
                        status_parts.append(f"📈 Current Status: {proj_status['status']}")
                        if proj_status.get("completion_percentage"):
                            status_parts.append(f"🎯 Progress: {proj_status['completion_percentage']}% complete")

                        if proj_status.get("blockers"):
                            blocker_count = len(proj_status["blockers"])
                            status_parts.append(f"🚫 {blocker_count} active blockers need attention")

                # Get TODO list
                todo_result = await self.mcp_tools.execute_tool("documentation", "get_todo_list")
                if todo_result["success"]:
                    todos = todo_result["result"]
                    total_items = todos.get("total_items", 0)
                    if total_items > 0:
                        status_parts.append(f"📋 {total_items} items in project TODO list")

            status_parts.append(f"\n💬 I'm actively monitoring the project and ready to help with your next steps.")

            return "\n".join(status_parts)

        except Exception as e:
            return f"I'm currently monitoring the project but encountered an issue getting detailed status: {str(e)}"

    async def _handle_feature_request(self, request: str, analysis: Dict[str, Any]) -> str:
        """Handle feature requests by creating specifications and tasks."""
        try:
            response_parts = []
            response_parts.append(f"🎯 **Feature Request: {request}**")

            # Create specification using documentation tools
            if "documentation" in self.mcp_tools.tools:
                # Extract feature details
                feature_title = request.replace("add ", "").replace("create ", "").replace("implement ", "").strip()
                feature_title = feature_title.replace("a ", "").replace("an ", "").title()

                # Create specification
                spec_result = await self.mcp_tools.execute_tool("documentation", "create_specification",
                    title=feature_title,
                    description=f"User request: {request}\n\nThis feature was requested by the founder and needs detailed analysis and implementation planning.",
                    requirements=[
                        "Analyze technical requirements",
                        "Design user interface/experience",
                        "Implement core functionality",
                        "Add comprehensive testing",
                        "Update documentation"
                    ],
                    spec_type="feature"
                )

                if spec_result["success"]:
                    spec = spec_result["result"]
                    response_parts.append(f"📋 I've created a detailed specification: `{spec['file_path']}`")

                # Create GitHub issue if repository is connected
                if "github" in self.mcp_tools.tools and self.repo_url:
                    await self.mcp_tools.execute_tool("github", "set_repository", repo_url=self.repo_url)

                    issue_result = await self.mcp_tools.execute_tool("github", "create_issue",
                        title=f"Feature: {feature_title}",
                        body=f"**User Request:** {request}\n\n**Specification:** See `docs/{spec.get('file_path', 'specification')}`\n\n**Priority:** {analysis.get('priority', 'medium')}\n\n**Complexity:** {analysis.get('estimated_complexity', 'moderate')}",
                        labels=["enhancement", "feature-request"]
                    )

                    if issue_result["success"]:
                        issue = issue_result["result"]
                        response_parts.append(f"🎫 Created GitHub issue #{issue['issue_number']}: {issue['url']}")

                # Update project TODO list
                todo_result = await self.mcp_tools.execute_tool("documentation", "update_todo_list",
                    items=[{
                        "title": f"Implement {feature_title}",
                        "description": f"Complete the {feature_title} feature as specified",
                        "priority": analysis.get("priority", "medium"),
                        "status": "pending"
                    }]
                )

                if todo_result["success"]:
                    response_parts.append("📝 Added to project TODO list for team coordination")

            response_parts.append(f"\n✅ I've prepared everything for the development team to implement this feature. The specification provides clear requirements and the GitHub issue will track progress.")

            # Document this as a strategic decision
            self.add_decision(
                f"Feature Planning: {feature_title}",
                f"Approved and planned implementation of {feature_title} feature",
                f"User request prioritized as {analysis.get('priority', 'medium')} priority based on strategic value"
            )

            return "\n".join(response_parts)

        except Exception as e:
            return f"I encountered an issue while planning the feature: {str(e)}"

    async def _handle_documentation_request(self, request: str, analysis: Dict[str, Any]) -> str:
        """Handle documentation-related requests."""
        try:
            response_parts = []
            response_parts.append(f"📚 **Documentation Request: {request}**")

            if "documentation" in self.mcp_tools.tools:
                # Create or update documentation
                if "readme" in request.lower():
                    response_parts.append("📄 I'll help update the README to better reflect our current project status.")

                    # Get current project overview for README update
                    overview_result = await self.mcp_tools.execute_tool("filesystem", "get_project_overview")
                    if overview_result["success"]:
                        response_parts.append("✅ Analyzed current project structure for README updates")

                elif "progress" in request.lower() or "report" in request.lower():
                    # Create progress report
                    report_result = await self.mcp_tools.execute_tool("documentation", "create_progress_report", report_type="weekly")
                    if report_result["success"]:
                        report = report_result["result"]
                        response_parts.append(f"📊 Created comprehensive progress report: `{report['file_path']}`")
                        response_parts.append("\n" + report["content"][:500] + "..." if len(report["content"]) > 500 else report["content"])

                else:
                    # General documentation improvement
                    response_parts.append("📋 I'll ensure our project documentation is comprehensive and up-to-date.")

            return "\n".join(response_parts)

        except Exception as e:
            return f"I encountered an issue with the documentation request: {str(e)}"

    async def _handle_coordination_request(self, request: str, analysis: Dict[str, Any]) -> str:
        """Handle team coordination requests."""
        try:
            response_parts = []
            response_parts.append(f"👥 **Team Coordination: {request}**")

            if "documentation" in self.mcp_tools.tools:
                # Add team message
                message_result = await self.mcp_tools.execute_tool("documentation", "add_team_message",
                    message=f"Founder request: {request}",
                    channel="ceo-announcements",
                    message_type="announcement"
                )

                if message_result["success"]:
                    response_parts.append("📢 Added to team communication channel for coordination")

                # Update project status if needed
                if "status" in request.lower() or "update" in request.lower():
                    status_result = await self.mcp_tools.execute_tool("documentation", "update_project_status",
                        status="active",
                        description=f"CEO coordinating team activities based on founder request: {request}",
                        completion_percentage=None
                    )

                    if status_result["success"]:
                        response_parts.append("📈 Updated project status for team visibility")

            response_parts.append("✅ Team has been notified and will coordinate accordingly.")

            return "\n".join(response_parts)

        except Exception as e:
            return f"I encountered an issue with team coordination: {str(e)}"

    async def clone_and_setup_repo(self) -> Dict[str, Any]:
        """Clone GitHub repository into workspace for development work."""
        if not self.mcp_tools or not self.repo_url:
            return {"success": False, "error": "Repository URL not available"}

        try:
            # Use git tools to clone repository
            clone_result = await self.mcp_tools.execute_tool("git", "clone_repository", repo_url=self.repo_url)

            if clone_result["success"]:
                # Set up GitHub coordination tools
                await self.mcp_tools.execute_tool("github", "set_repository", repo_url=self.repo_url)

                # Analyze the cloned repository
                analysis_result = await self.mcp_tools.execute_tool("filesystem", "analyze_project_structure")

                # Document the setup
                if analysis_result["success"]:
                    await self.mcp_tools.execute_tool("documentation", "document_decision",
                        title="Repository Cloned and Analyzed",
                        description=f"Successfully cloned {self.repo_url} into workspace",
                        rationale="Enables CEO to perform hands-on project coordination and oversight",
                        impact="CEO can now analyze code, make updates, and coordinate development activities"
                    )

                return {
                    "success": True,
                    "repo_cloned": True,
                    "analysis": analysis_result.get("result") if analysis_result["success"] else None
                }

            return clone_result

        except Exception as e:
            return {"success": False, "error": str(e)}