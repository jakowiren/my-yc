"""
MCP Tools for AI Agents
Model Context Protocol tools for CEO and team coordination.
"""

from .base_mcp import BaseMCPTool, MCPToolRegistry, MCPToolError
from .filesystem_tools import FileSystemMCP
from .git_tools import GitMCP
from .documentation_tools import DocumentationMCP
from .github_coordination_tools import GitHubCoordinationMCP
from .github_tools import GitHubMCPTools  # Legacy tool

__all__ = [
    'BaseMCPTool',
    'MCPToolRegistry',
    'MCPToolError',
    'FileSystemMCP',
    'GitMCP',
    'DocumentationMCP',
    'GitHubCoordinationMCP',
    'GitHubMCPTools'
]