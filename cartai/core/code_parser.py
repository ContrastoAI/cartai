"""
Code parsing utilities for CartAI.

This module provides functionality to parse and analyze code projects,
extracting structural information while optimizing for token efficiency.
"""

from pathlib import Path
from typing import Any, Set, Union, Literal
import re
from pydantic import BaseModel, Field, ConfigDict

from cartai.llm_agents.graph_states import CartaiDynamicState


class ParsedBase(BaseModel):
    """Base class for parsed items with shared fields."""

    type: str
    name: str
    path: Path
    error: str | None = None


class ParsedDirectory(ParsedBase):
    """A parsed directory with its contents."""

    type: Literal["directory"] = "directory"
    contents: list["ParsedItem"]


class ParsedFile(ParsedBase):
    """A parsed file with its contents."""

    type: Literal["file"] = "file"
    extension: str
    size_kb: float
    entities: dict[str, list[str]]
    content: str
    error: str | None = None


ParsedItem = Union[ParsedDirectory, ParsedFile]


class ParsedFileDiscriminator(ParsedDirectory):
    model_config = {
        "json_schema_extra": {
            "discriminator": "type",
            "mapping": {"directory": "ParsedDirectory", "file": "ParsedFile"},
        }
    }


class ProjectParser(BaseModel):
    """
    Parser for code projects that extracts structural information efficiently.

    This class recursively scans a project directory, analyzing files and folders
    while optimizing the output to minimize token usage when feeding to LLMs.
    Can be used as a LangGraph node.
    """

    project_path: Union[str, Path] = Field(
        default=".",
        description="Path to the project directory to parse",
    )
    ignore_dirs: Set[str] = Field(
        default={
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".pytest_cache",
            ".pdm-build",
            "examples",
            "tests",
        },
        description="Directory names to ignore",
    )
    ignore_files: Set[str] = Field(
        default={".DS_Store", ".gitignore", "package-lock.json", "yarn.lock", ".env"},
        description="File names to ignore",
    )
    ignore_extensions: Set[str] = Field(
        default={".pyc", ".pyo", ".pyd", ".so", ".dll", ".class", ".log"},
        description="File extensions to ignore",
    )
    full_content_files: Set[str] = Field(
        default={".md", ".txt", ".yaml", ".toml", ""},
        description="File extensions to include full content for",
    )
    max_file_size_kb: int = Field(
        default=100, description="Maximum file size in KB to include content for"
    )
    include_basic_entities: bool = Field(
        default=True,
        description="Whether to extract basic entities like classes and functions",
    )
    include_full_content: bool = Field(
        default=False,
        description="Whether to include complete file content in the output",
    )
    # summarize_large_files: bool = Field(
    #    default=True,
    #    description="Whether to include summaries for large files"
    # )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def parse(self, path: Union[str, Path]) -> dict[str, Any]:
        """
        Parse a project directory and return its structure.

        Args:
            path: Path to the project directory

        Returns:
            Dict containing the project structure with files and directories
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if path.is_file():
            return (await self._parse_file(path)).model_dump()

        return (await self._parse_directory(path)).model_dump()

    async def _parse_directory(self, path: Path) -> ParsedDirectory:
        """Parse a directory and its contents recursively."""
        result = ParsedDirectory(
            name=path.name,
            path=path,
            contents=[],
        )

        try:
            for item in sorted(path.iterdir()):
                # Skip ignored directories and files
                if (item.is_dir() and item.name in self.ignore_dirs) or (
                    item.is_file()
                    and (
                        item.name in self.ignore_files
                        or item.suffix in self.ignore_extensions
                    )
                ):
                    continue

                if item.is_dir():
                    result.contents.append(await self._parse_directory(item))
                else:
                    file_info = await self._parse_file(item)
                    if file_info:
                        result.contents.append(file_info)
        except PermissionError:
            result.error = "Permission denied"

        return result

    async def _parse_file(self, path: Path) -> ParsedFile:
        """Parse a single file and extract relevant information."""
        file_size_kb = path.stat().st_size / 1024

        result = ParsedFile(
            name=path.name,
            path=path,
            entities={},
            content="",
            extension=path.suffix,
            size_kb=round(file_size_kb, 2),
        )

        # Skip files that are too large
        # if file_size_kb > self.max_file_size_kb:
        #    if self.summarize_large_files:
        #        result["note"] = f"Large file ({result['size_kb']} KB), content omitted"
        #    return result

        try:
            # Use aiofiles for async file reading
            content = await self._read_file_async(path)

            # Extract basic entities if requested
            if self.include_basic_entities and path.suffix in {
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".hpp",
                ".h",
                ".c",
            }:
                entities = self._extract_basic_entities(content, path.suffix)
                if entities:
                    result.entities = entities

            # Include full file content if requested
            elif self.include_full_content:
                result.content = content

            if path.suffix in self.full_content_files:
                result.content = content

        except Exception as e:
            result.error = f"Could not read file: {str(e)}"

        return result

    async def _read_file_async(self, path: Path) -> str:
        """Helper method to read file content asynchronously."""
        import aiofiles

        async with aiofiles.open(path, mode="r", errors="replace") as f:
            return await f.read()

    def _extract_basic_entities(
        self, content: str, extension: str
    ) -> dict[str, list[str]]:
        """Extract basic entities (classes, functions) from code content."""
        entities: dict[str, list[str]] = {"classes": [], "functions": []}

        if extension == ".py":
            # Python patterns
            class_pattern = r"class\s+([a-zA-Z_]\w*)"
            func_pattern = r"def\s+([a-zA-Z_]\w*)"
        elif extension in {".js", ".ts"}:
            # JavaScript/TypeScript patterns
            class_pattern = r"class\s+([a-zA-Z_]\w*)"
            func_pattern = r"function\s+([a-zA-Z_]\w*)|const\s+([a-zA-Z_]\w*)\s*="
        elif extension in {".java"}:
            # Java patterns
            class_pattern = r"class\s+([a-zA-Z_]\w*)"
            func_pattern = r"(?:public|private|protected)?\s+(?:static\s+)?[a-zA-Z_]\w*\s+([a-zA-Z_]\w*)\s*\("
        elif extension in {".cpp", ".hpp", ".h", ".c"}:
            # C/C++ patterns
            class_pattern = r"class\s+([a-zA-Z_]\w*)"
            func_pattern = r"[a-zA-Z_]\w*\s+([a-zA-Z_]\w*)\s*\("
        else:
            return entities

        # Extract classes
        classes = re.findall(class_pattern, content)
        if classes:
            entities["classes"] = list(set(classes))

        # Extract functions
        functions = re.findall(func_pattern, content)
        if functions:
            # Handle tuple results from regex groups
            if isinstance(functions[0], tuple):
                functions = [f[0] or f[1] for f in functions]
            entities["functions"] = list(set(functions))

        return entities if (entities["classes"] or entities["functions"]) else {}

    async def get_summary(self, path: Union[str, Path]) -> str:
        """
        Generate a token-efficient summary of the project structure.

        Args:
            path: Path to the project directory

        Returns:
            A string representation of the project structure optimized for LLM consumption
        """
        path = Path(path)
        structure = await self.parse(path)

        return self._format_summary(structure)

    def _format_summary(self, structure: dict[str, Any], indent: int = 0) -> str:
        """Format the structure dictionary as a string with proper indentation."""
        result = []

        if structure["type"] == "directory":
            result.append(f"{'  ' * indent}📁 {structure['name']}/")
            for item in structure.get("contents", []):
                result.append(self._format_summary(item, indent + 1))
        else:  # file
            file_info = f"{'  ' * indent}📄 {structure['name']}"
            if structure["error"]:
                file_info += f" ({structure['error']})"
            result.append(file_info)

        return "\n".join(result)

    async def run(self, state: dict[str, Any]) -> CartaiDynamicState:
        """
        Run the parser as a LangGraph node.

        Args:
            state: The current state containing project context

        Returns:
            Updated state with project structure information
        """
        if not self.project_path:
            self.project_path = state.get("project_path", ".")

        try:
            structure = await self.parse(self.project_path)
            return {
                "messages": [1],
                "outputs": [("ProjectStructure", structure)],
                "project_context": {
                    **(state.get("project_context", {})),
                    "structure": structure,
                },
            }
        except Exception as e:
            return {
                "messages": [0],
                "outputs": [("ProjectStructure_Error", str(e))],
                "project_context": state.get("project_context", {}),
            }
