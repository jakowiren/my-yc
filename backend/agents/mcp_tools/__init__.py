"""
MCP Tools for AI Agents
Model Context Protocol tools for CEO and team coordination.
"""

from mcp_tools.base_mcp import BaseMCPTool, MCPToolRegistry, MCPToolError
from mcp_tools.filesystem_tools import FileSystemMCP
from mcp_tools.git_tools import GitMCP
from mcp_tools.documentation_tools import DocumentationMCP
from mcp_tools.github_coordination_tools import GitHubCoordinationMCP
from mcp_tools.github_tools import GitHubMCPTools  # Legacy tool
from mcp_tools.team_tools import TeamToolsMCP

__all__ = [
    'BaseMCPTool',
    'MCPToolRegistry',
    'MCPToolError',
    'FileSystemMCP',
    'GitMCP',
    'DocumentationMCP',
    'GitHubCoordinationMCP',
    'GitHubMCPTools',
    'TeamToolsMCP'
]