# MCP Tools for CEO Agents

This directory contains the Model Context Protocol (MCP) tool implementations for CEO agents to interact with their development environment.

## Current Structure

```
mcp_tools/
├── __init__.py          # Tool registry and imports
├── github_tools.py      # GitHub API integration (Phase 1)
└── README.md           # This documentation
```

## Existing Tools

### github_tools.py (Phase 1)
- **Purpose**: Direct GitHub API integration for repository management
- **Status**: Implemented for CEO initialization
- **Features**: Repository creation, README updates, basic Git operations
- **Usage**: Embedded directly in CEO agents via PyGithub

## Phase 2 Integration Strategy

### Planned Tool Categories

1. **Filesystem Tools** (`filesystem_tools.py`)
   - File read/write operations within workspace
   - Directory navigation and management
   - Safe file operations with workspace boundaries

2. **Git Tools** (`git_tools.py`)
   - Git operations within cloned repositories
   - Branch management, commits, merges
   - Integration with GitHub tools for remote operations

3. **Terminal Tools** (`terminal_tools.py`)
   - Command execution within workspace containers
   - Build system integration (npm, cargo, etc.)
   - Environment setup and dependency management

4. **Enhanced GitHub Tools** (`github_tools.py` - extended)
   - Issue management and project boards
   - Pull request creation and management
   - Advanced repository analytics

5. **Workspace Tools** (`workspace_tools.py`)
   - Workspace metadata management
   - Agent coordination and communication
   - Task queue and progress tracking

### Architecture Principles

1. **Workspace Isolation**: All tools operate within startup-specific workspaces (`/workspace/{startup_id}/`)
2. **Safety First**: All operations are sandboxed and logged
3. **Persistent State**: Tool usage is logged for CEO memory and learning
4. **Agent Coordination**: Tools support multi-agent collaboration

### Integration with CEO Agents

```python
# CEO agents will use tools via workspace manager
class CEOAgent:
    def __init__(self, startup_id, design_doc, workspace_mgr):
        self.workspace_mgr = workspace_mgr
        self.tools = MCPToolRegistry(workspace_mgr, startup_id)

    async def use_tool(self, tool_name: str, **kwargs):
        return await self.tools.execute(tool_name, **kwargs)
```

### Tool Execution Flow

1. **Request**: CEO receives task requiring tool usage
2. **Authorization**: Verify tool access within workspace boundaries
3. **Execution**: Run tool with logging and error handling
4. **Persistence**: Save tool usage to conversation history
5. **Response**: Return results to CEO for integration

## Implementation Timeline

- **Phase 1**: ✅ Basic GitHub integration (completed)
- **Phase 2**: 🔄 Full MCP tool suite (5 days estimated)
- **Phase 3**: 📋 Advanced coordination tools

## Security Considerations

- All file operations restricted to workspace directories
- Command execution in sandboxed Modal containers
- API keys managed via Modal secrets
- Destructive operations require explicit confirmation
- Complete audit trail of all tool usage

## Development Notes

The existing `github_tools.py` will be extended rather than replaced, maintaining compatibility with current CEO initialization while adding the broader MCP framework for Phase 2.