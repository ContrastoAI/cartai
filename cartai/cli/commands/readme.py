"""
README generation command implementation
"""

from cartai.llm_agents.graph import CartaiGraph
from cartai.llm_agents.graph_states import CartaiDynamicState
import typer
import asyncio
from rich.console import Console

console = Console()


async def async_langgraph_readme_command():
    graph = CartaiGraph(config_file="langgraph_config/repo_documenter.yaml")
    await graph.ainvoke(CartaiDynamicState(messages=["0"]))

def readme_command(
    description: str = typer.Option(..., help="Short description of the project"),
    code: str = typer.Option(".", help="Path to the code directory"),
    output: str = typer.Option("README.md", help="Output file path"),
    dry_run: bool = typer.Option(
        False, help="Print the README to stdout instead of writing to a file"
    ),
):
    """Generate a README.md file for the project."""
    
    asyncio.run(async_langgraph_readme_command())
