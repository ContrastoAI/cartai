"""
README generation command implementation
"""

import typer
from rich.console import Console
from cartai.core.code_parser import ProjectParser
from cartai.llm_agents.documenter import AIDocumenter

console = Console()


def readme_command(
    description: str = typer.Option(..., help="Short description of the project"),
    code: str = typer.Option(".", help="Path to the code directory"),
    output: str = typer.Option("README.md", help="Output file path"),
    dry_run: bool = typer.Option(
        False, help="Print the README to stdout instead of writing to a file"
    ),
):
    """Generate a README.md file for the project."""
    console.print("[bold green]Crafting README[/]")
    console.print(f"Using code from: {code}")

    parser = ProjectParser(
        include_basic_entities=True,
    )

    summary = parser.get_summary(code)
    console.print(f"Structure: {summary}")

    full_structure = parser.parse(code)
    console.print(f"Description: {description}")

    documenter = AIDocumenter()

    result = documenter.generate(
        "readme.jinja",
        {
            "description": description,
            "structure": f"Repo summary structure: {summary}. Repo files:{full_structure}",
        },
    )

    if dry_run:
        console.print(result)
    else:
        # Use UTF-8 encoding when writing the file
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)

        console.print(f"[bold green]README created at[/] [bold yellow]{output}[/]")
