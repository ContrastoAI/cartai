"""
PR diff analysis command implementation
"""

import typer
import os
import subprocess
import requests
import fnmatch

from rich.console import Console

console = Console()

EXCLUDE_PATTERNS = [
    "*.md",
    "*.lock",
    "yarn.lock",
    "package-lock.json",
    ".env",
    "*.png",
    "*.jpg",
]
MAX_DIFF_CHARS = int(os.getenv("MAX_DIFF_CHARS", 6000))  # Trim large diffs
GH_TOKEN = os.getenv("GH_TOKEN")


def _is_excluded(filepath):
    return any(fnmatch.fnmatch(filepath, pattern) for pattern in EXCLUDE_PATTERNS)


def _get_filtered_diff():
    # return subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode("utf-8")
    raw_diff = subprocess.check_output(
        ["git", "diff", "--name-only", "origin/main...HEAD"]
    ).decode("utf-8")
    files = [
        f.strip()
        for f in raw_diff.splitlines()
        if f.strip() and not _is_excluded(f.strip())
    ]
    if not files:
        return ""
    diff = subprocess.check_output(
        ["git", "diff", "origin/main...HEAD", "--", *files]
    ).decode("utf-8")
    return diff[:MAX_DIFF_CHARS]  # Trim long diffs


def pr_diff_command(
    pr_number: int | None = typer.Option(
        None, help="Pull request number to analyze"
    ),
    repo: str | None = typer.Option(
        None, help="Repository name in format owner/repo (optional if in a git repo)"
    ),
):
    """Analyze code changes in a pull request and generate a summary."""

    diff = _get_filtered_diff()

    if not diff.strip():
        print("No relevant diff to summarize.")
        exit(0)

    # === Call the LLM ===
    from cartai.llm_agents.documenter import AIDocumenter

    documenter = AIDocumenter()
    summary = documenter.generate(
        "pr_diff.jinja",
        {
            "pr_title": "Add new feature",
            "description": "Add a new feature to the project",
            "diff": diff,
        },
    )

    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_data = requests.get(pr_url, headers=headers).json()
    original_body: str = pr_data.get("body", "") or ""

    if "### Summarized changes" in original_body:
        new_body = original_body.split("### Summarized changes")[0].strip()
    else:
        new_body = original_body.strip()

    new_body += f"\n\n### Summarized changes\n{summary}"

    requests.patch(pr_url, headers=headers, json={"body": new_body})
    print("PR description updated with summary.")


def pr_diff_command_mock(
    pr_number: int | None = typer.Option(
        None, help="Pull request number to analyze"
    ),
    repo: str | None = typer.Option(
        None, help="Repository name in format owner/repo (optional if in a git repo)"
    ),
    output: str = typer.Option("pr_diff_analysis.md", help="Output file path"),
    dry_run: bool = typer.Option(
        False, help="Print the analysis to stdout instead of writing to a file"
    ),
):
    """Analyze code changes in a pull request and generate a summary."""
    console.print("[bold green]Analyzing PR diff[/]")
    console.print(f"PR #{pr_number}" + (f" in repo {repo}" if repo else ""))

    # TODO: Implement PR diff analysis
    # 1. Fetch the PR diff from GitHub
    # 2. Parse the changes
    # 3. Generate an analysis

    result = (
        f"# PR #{pr_number} Analysis\n\nThis is a placeholder for PR diff analysis."
    )

    if dry_run:
        console.print(result)
    else:
        # Use UTF-8 encoding when writing the file
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)

        console.print(f"[bold green]PR analysis created at[/] [bold yellow]{output}[/]")
