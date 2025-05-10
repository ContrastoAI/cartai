"""
PR diff analysis command implementation
"""

import typer
from rich.console import Console

console = Console()


def pr_diff_command(
    pull_request: int = typer.Option(..., help="Pull request number to analyze"),
    repo: str = typer.Option(
        None, help="Repository name in format owner/repo (optional if in a git repo)"
    ),
    output: str = typer.Option("pr_diff_analysis.md", help="Output file path"),
    dry_run: bool = typer.Option(
        False, help="Print the analysis to stdout instead of writing to a file"
    ),
):
    """Analyze code changes in a pull request and generate a summary."""
    console.print("[bold green]Analyzing PR diff[/]")
    console.print(f"PR #{pull_request}" + (f" in repo {repo}" if repo else ""))

    # TODO: Implement PR diff analysis
    # 1. Fetch the PR diff from GitHub
    # 2. Parse the changes
    # 3. Generate an analysis

    result = (
        f"# PR #{pull_request} Analysis\n\nThis is a placeholder for PR diff analysis."
    )

    if dry_run:
        console.print(result)
    else:
        # Use UTF-8 encoding when writing the file
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)

        console.print(f"[bold green]PR analysis created at[/] [bold yellow]{output}[/]")
