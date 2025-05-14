"""
PR diff analysis command implementation
"""

import typer
import os
import subprocess
import requests
import fnmatch

from rich.console import Console
from cartai.llm_agents.documenter import AIDocumenter

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
    try:
        # Try local git diff first
        raw_diff = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main...HEAD"]
        ).decode("utf-8")
    except subprocess.CalledProcessError:
        # Fallback for CI: fetch main branch first
        subprocess.run(["git", "fetch", "origin", "main:main"], check=True)
        raw_diff = subprocess.check_output(
            ["git", "diff", "--name-only", "main...HEAD"]
        ).decode("utf-8")

    files = [
        f.strip()
        for f in raw_diff.splitlines()
        if f.strip() and not _is_excluded(f.strip())
    ]
    if not files:
        return ""

    try:
        diff = subprocess.check_output(
            ["git", "diff", "origin/main...HEAD", "--", *files]
        ).decode("utf-8")
    except subprocess.CalledProcessError:
        diff = subprocess.check_output(
            ["git", "diff", "main...HEAD", "--", *files]
        ).decode("utf-8")

    return diff[:MAX_DIFF_CHARS]


async def pr_diff_command(
    pr_number: int | None = typer.Option(None, help="Pull request number to analyze"),
    repo: str | None = typer.Option(
        None, help="Repository name in format owner/repo (optional if in a git repo)"
    ),
):
    """Analyze code changes in a pull request and generate a summary."""

    diff = _get_filtered_diff()

    if not diff.strip():
        print("No relevant diff to summarize.")
        exit(0)

    documenter = AIDocumenter()
    summary = await documenter.generate(
        template_name="pr_diff.jinja",
        context={
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
