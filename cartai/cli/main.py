#!/usr/bin/env python3
"""
CartAI CLI - A tool for crafting documentation from code.
"""

import typer
from rich.console import Console
from cartai.cli.commands.readme import readme_command
from cartai.cli.commands.pr_diff import pr_diff_command


app = typer.Typer(help="CartAI - AI-powered documentation tools.")
console = Console()


@app.command(name="readme")
def readme(
    description: str = typer.Option(..., help="Short description of the project"),
    code: str = typer.Option(".", help="Path to the code directory"),
    output: str = typer.Option("README.md", help="Output file path"),
    dry_run: bool = typer.Option(
        False, help="Print the README to stdout instead of writing to a file"
    ),
):
    """Generate a README.md file for the project."""
    readme_command(description=description, code=code, output=output, dry_run=dry_run)


@app.command(name="pr-diff")
def pr_diff(
    pull_request: int | None = typer.Option(
        None, help="Pull request number to analyze"
    ),
    repo: str | None = typer.Option(
        None, help="Repository name in format owner/repo (optional if in a git repo)"
    ),
    output: str | None = typer.Option("pr_diff_analysis.md", help="Output file path"),
    dry_run: bool | None = typer.Option(
        False, help="Print the analysis to stdout instead of writing to a file"
    ),
):
    """Analyze code changes in a pull request and generate a summary."""
    pr_diff_command(
        pull_request=pull_request, repo=repo, output=output, dry_run=dry_run
    )


@app.callback()
def callback():
    """
    CartAI - AI-powered documentation tools.
    """
