#!/usr/bin/env python3
"""
CartAI CLI - A tool for crafting documentation from code.
"""

from cartai.llm_agents.documenter import AIDocumenter
import typer
from rich.console import Console


app = typer.Typer(help="CartAI - AI-powered documentation tools.")
console = Console()


@app.command()
def readme(
    description: str = typer.Option(..., "--description", "-d", help="Project description"),
    code_path: str = typer.Option(None, "--code", "-c", help="Path to code directory"),
    output: str = typer.Option("README.md", "--output", "-o", help="Output file path")
):
    """Generate a README file based on description and code."""
    console.print(f"[bold green]Crafting README[/]")
    if code_path:
        console.print(f"[bold blue]Using code from:[/] {code_path}")
    console.print(f"[bold blue]Description:[/] {description}")
    
    documenter = AIDocumenter()
    result = documenter.generate(
        template_name="readme.jinja",
        context={
            "description": description,
            "structure": code_path
        }
    )
    
    with open(output, "w") as f:
        f.write(result)
    
    console.print(f"[bold green]README created at[/] [bold yellow]{output}[/]")


#def main():
#    """Main entry point for the CLI."""
#    try:
#        app()
#    except Exception as e:
#        console.print(f"[bold red]Error:[/] {str(e)}")
#        raise typer.Exit(1)
