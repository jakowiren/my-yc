"""
File System MCP Tools
CEO-focused file operations for understanding and documenting projects.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base_mcp import BaseMCPTool, MCPToolError, openai_function


class FileSystemMCP(BaseMCPTool):
    """
    File system operations for CEO strategic oversight.

    Focus: Understanding codebase, creating documentation, managing project files.
    NOT for complex coding - that's for specialist agents in Phase 3.
    """

    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute file system action."""
        action_map = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_directory": self.list_directory,
            "create_directory": self.create_directory,
            "get_project_overview": self.get_project_overview,
            "analyze_project_structure": self.analyze_project_structure,
            "search_files": self.search_files
        }

        if action not in action_map:
            raise MCPToolError(f"Unknown action: {action}")

        return await action_map[action](**kwargs)

    @openai_function("read_file", "Read contents of a specific file", {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file to read"},
            "max_lines": {"type": "integer", "description": "Maximum lines to read (optional)"}
        },
        "required": ["file_path"]
    })
    async def read_file(self, file_path: str, max_lines: Optional[int] = None) -> Dict[str, Any]:
        """
        Read a file for CEO understanding.

        Args:
            file_path: Path to file (relative to workspace)
            max_lines: Maximum lines to read (for large files)

        Returns:
            File content, metadata, and analysis
        """
        try:
            validated_path = self._validate_path(file_path)

            if not validated_path.exists():
                return {"error": f"File not found: {file_path}"}

            if not validated_path.is_file():
                return {"error": f"Path is not a file: {file_path}"}

            # Read file content
            try:
                with open(validated_path, 'r', encoding='utf-8') as f:
                    if max_lines:
                        lines = []
                        for i, line in enumerate(f):
                            if i >= max_lines:
                                break
                            lines.append(line.rstrip())
                        content = '\n'.join(lines)
                        truncated = True
                    else:
                        content = f.read()
                        truncated = False
            except UnicodeDecodeError:
                # Try reading as binary for non-text files
                with open(validated_path, 'rb') as f:
                    first_bytes = f.read(100)
                    return {
                        "file_path": file_path,
                        "file_type": "binary",
                        "size_bytes": validated_path.stat().st_size,
                        "preview": f"Binary file: {first_bytes.hex()[:40]}..."
                    }

            # Analyze file for CEO context
            file_analysis = self._analyze_file_content(validated_path, content)

            return {
                "file_path": file_path,
                "content": content,
                "truncated": truncated if max_lines else False,
                "file_type": file_analysis["file_type"],
                "line_count": len(content.split('\n')) if content else 0,
                "size_bytes": validated_path.stat().st_size,
                "last_modified": validated_path.stat().st_mtime,
                "analysis": file_analysis
            }

        except Exception as e:
            self.log_activity("read_file_error", {"file_path": file_path, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to read file: {str(e)}")

    @openai_function("write_file", "Write content to a file (creates or overwrites)", {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file to write"},
            "content": {"type": "string", "description": "Content to write to the file"}
        },
        "required": ["file_path", "content"]
    })
    async def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
        """
        Write file content (primarily for documentation and configs).

        Args:
            file_path: Path to file (relative to workspace)
            content: Content to write
            create_dirs: Create parent directories if needed

        Returns:
            Write operation result
        """
        try:
            validated_path = self._validate_path(file_path)

            # Create parent directories if needed
            if create_dirs:
                validated_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(validated_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Log the write operation
            self.log_activity("file_written", {
                "file_path": file_path,
                "content_length": len(content),
                "purpose": "ceo_documentation"
            })

            return {
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "created": not validated_path.existed() if hasattr(validated_path, 'existed') else True
            }

        except Exception as e:
            self.log_activity("write_file_error", {"file_path": file_path, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to write file: {str(e)}")

    async def list_directory(self, dir_path: str = ".", show_hidden: bool = False,
                           include_analysis: bool = True) -> Dict[str, Any]:
        """
        List directory contents with CEO-relevant analysis.

        Args:
            dir_path: Directory path (relative to workspace)
            show_hidden: Include hidden files/directories
            include_analysis: Include project structure analysis

        Returns:
            Directory listing with analysis
        """
        try:
            validated_path = self._validate_path(dir_path)

            if not validated_path.exists():
                return {"error": f"Directory not found: {dir_path}"}

            if not validated_path.is_dir():
                return {"error": f"Path is not a directory: {dir_path}"}

            items = []
            for item in sorted(validated_path.iterdir()):
                if not show_hidden and item.name.startswith('.'):
                    continue

                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size_bytes": item.stat().st_size if item.is_file() else None,
                    "last_modified": item.stat().st_mtime
                }

                if item.is_file():
                    item_info["file_type"] = self._get_file_type(item)

                items.append(item_info)

            result = {
                "directory": dir_path,
                "items": items,
                "total_items": len(items),
                "directories": len([i for i in items if i["type"] == "directory"]),
                "files": len([i for i in items if i["type"] == "file"])
            }

            if include_analysis and dir_path in [".", ""]:
                result["project_analysis"] = await self._analyze_directory_structure(validated_path)

            return result

        except Exception as e:
            self.log_activity("list_directory_error", {"dir_path": dir_path, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to list directory: {str(e)}")

    async def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """Create directory for organizing project files."""
        try:
            validated_path = self._validate_path(dir_path)
            validated_path.mkdir(parents=True, exist_ok=True)

            self.log_activity("directory_created", {"dir_path": dir_path})

            return {
                "directory": dir_path,
                "created": True,
                "absolute_path": str(validated_path)
            }

        except Exception as e:
            self.log_activity("create_directory_error", {"dir_path": dir_path, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to create directory: {str(e)}")

    @openai_function("get_project_overview", "Get overview of the project including repository status, file count, and workspace info")
    async def get_project_overview(self) -> Dict[str, Any]:
        """
        Get high-level project overview for CEO understanding.

        Returns:
            Comprehensive project overview
        """
        try:
            overview = {
                "workspace_path": str(self.workspace),
                "startup_id": self.startup_id,
                "github_repo_status": "present" if self.github_repo_path.exists() else "not_cloned"
            }

            # Analyze github repo if present
            if self.github_repo_path.exists():
                repo_analysis = await self._analyze_directory_structure(self.github_repo_path)
                overview["repository_analysis"] = repo_analysis

            # Check for key project files
            overview["key_files"] = await self._find_key_project_files()

            # Get documentation status
            overview["documentation_status"] = await self._analyze_documentation()

            return overview

        except Exception as e:
            self.log_activity("project_overview_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to get project overview: {str(e)}")

    async def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure to understand tech stack and organization."""
        try:
            if not self.github_repo_path.exists():
                return {"error": "No GitHub repository found to analyze"}

            analysis = await self._analyze_directory_structure(self.github_repo_path)
            return analysis

        except Exception as e:
            self.log_activity("analyze_structure_error", {"error": str(e)}, "error")
            raise MCPToolError(f"Failed to analyze project structure: {str(e)}")

    async def search_files(self, query: str, file_extension: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for files by name or content (simple text search).

        Args:
            query: Search query
            file_extension: Optional file extension filter

        Returns:
            Search results
        """
        try:
            search_root = self.github_repo_path if self.github_repo_path.exists() else self.workspace
            results = []

            for file_path in search_root.rglob("*"):
                if not file_path.is_file():
                    continue

                # Filter by extension if specified
                if file_extension and not file_path.name.endswith(file_extension):
                    continue

                # Search in filename
                if query.lower() in file_path.name.lower():
                    results.append({
                        "file": str(file_path.relative_to(search_root)),
                        "match_type": "filename",
                        "file_type": self._get_file_type(file_path)
                    })
                    continue

                # Search in content for text files
                if self._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append({
                                    "file": str(file_path.relative_to(search_root)),
                                    "match_type": "content",
                                    "file_type": self._get_file_type(file_path)
                                })
                    except:
                        pass  # Skip files that can't be read

            return {
                "query": query,
                "results": results[:20],  # Limit results
                "total_matches": len(results)
            }

        except Exception as e:
            self.log_activity("search_files_error", {"query": query, "error": str(e)}, "error")
            raise MCPToolError(f"Failed to search files: {str(e)}")

    # Helper methods

    def _analyze_file_content(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Analyze file content for CEO context."""
        file_type = self._get_file_type(file_path)

        analysis = {
            "file_type": file_type,
            "purpose": "unknown"
        }

        # Determine file purpose based on name and content
        filename = file_path.name.lower()

        if filename in ["readme.md", "readme.txt", "readme"]:
            analysis["purpose"] = "project_documentation"
        elif filename == "package.json":
            analysis["purpose"] = "dependency_management"
            if content:
                try:
                    pkg_data = json.loads(content)
                    analysis["project_name"] = pkg_data.get("name", "unknown")
                    analysis["dependencies"] = list(pkg_data.get("dependencies", {}).keys())
                except:
                    pass
        elif filename in [".env", ".env.example"]:
            analysis["purpose"] = "configuration"
        elif filename.endswith((".md", ".txt")):
            analysis["purpose"] = "documentation"
        elif filename.endswith((".js", ".ts", ".jsx", ".tsx")):
            analysis["purpose"] = "frontend_code"
        elif filename.endswith((".py", ".rb", ".php")):
            analysis["purpose"] = "backend_code"

        return analysis

    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension."""
        suffix = file_path.suffix.lower()

        type_map = {
            ".md": "markdown",
            ".txt": "text",
            ".json": "json",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "react",
            ".tsx": "react_typescript",
            ".py": "python",
            ".html": "html",
            ".css": "css",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".env": "environment"
        }

        return type_map.get(suffix, "unknown")

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file."""
        text_extensions = {".md", ".txt", ".json", ".js", ".ts", ".jsx", ".tsx",
                          ".py", ".html", ".css", ".yml", ".yaml", ".env", ".gitignore"}
        return file_path.suffix.lower() in text_extensions

    async def _analyze_directory_structure(self, root_path: Path) -> Dict[str, Any]:
        """Analyze directory structure to understand project type."""
        analysis = {
            "project_type": "unknown",
            "tech_stack": [],
            "structure": "unknown"
        }

        # Check for key indicator files
        key_files = {}
        for file_path in root_path.rglob("*"):
            if file_path.is_file():
                filename = file_path.name.lower()
                if filename in ["package.json", "requirements.txt", "cargo.toml", "go.mod", "composer.json"]:
                    key_files[filename] = file_path

        # Determine project type and tech stack
        if "package.json" in key_files:
            analysis["project_type"] = "javascript"
            analysis["tech_stack"].append("Node.js")

            # Try to determine if it's React, Next.js, etc.
            try:
                with open(key_files["package.json"], 'r') as f:
                    pkg_data = json.loads(f.read())
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

                    if "next" in deps:
                        analysis["tech_stack"].append("Next.js")
                    elif "react" in deps:
                        analysis["tech_stack"].append("React")

                    if "typescript" in deps or "@types/node" in deps:
                        analysis["tech_stack"].append("TypeScript")
            except:
                pass

        elif "requirements.txt" in key_files:
            analysis["project_type"] = "python"
            analysis["tech_stack"].append("Python")

        elif "cargo.toml" in key_files:
            analysis["project_type"] = "rust"
            analysis["tech_stack"].append("Rust")

        # Check directory structure
        dirs = [d.name for d in root_path.iterdir() if d.is_dir()]
        if "src" in dirs:
            analysis["structure"] = "src_based"
        elif "app" in dirs:
            analysis["structure"] = "app_based"

        return analysis

    async def _find_key_project_files(self) -> Dict[str, bool]:
        """Find key project files that CEO should know about."""
        key_files = {
            "README.md": False,
            "package.json": False,
            "requirements.txt": False,
            ".env.example": False,
            "docker-compose.yml": False,
            ".gitignore": False
        }

        search_root = self.github_repo_path if self.github_repo_path.exists() else self.workspace

        for file_name in key_files:
            file_path = search_root / file_name
            key_files[file_name] = file_path.exists()

        return key_files

    async def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze current documentation status."""
        docs_status = {
            "readme_exists": False,
            "docs_directory_exists": self.docs_path.exists(),
            "documentation_files": []
        }

        # Check for README in repo
        if self.github_repo_path.exists():
            readme_path = self.github_repo_path / "README.md"
            docs_status["readme_exists"] = readme_path.exists()

        # List documentation files in workspace
        if self.docs_path.exists():
            for doc_file in self.docs_path.glob("*.md"):
                docs_status["documentation_files"].append(doc_file.name)

        return docs_status