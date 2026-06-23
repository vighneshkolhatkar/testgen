from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from testgen.detector import detect_language
from testgen.generator.llm_client import stream_tests
from testgen.generator.prompt_builder import build_prompt
from testgen.output.writer import write_output
from testgen.parser.java_parser import JavaParser
from testgen.parser.python_parser import PythonParser

app = typer.Typer(
    help="Agentic test generator powered by Claude.",
    add_completion=False,
)
console = Console()


def _get_parser(language: str):
    return PythonParser() if language == "python" else JavaParser()


@app.command()
def generate(
    file: str = typer.Argument(..., help="Path to source file (.py or .java)"),
    function: Optional[str] = typer.Option(
        None, "--function", "-f", help="Target a specific function or method name"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output directory for generated test file"
    ),
    fast: bool = typer.Option(False, "--fast", help="Use Claude Haiku (faster, cheaper)"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show parsed context without calling the API"
    ),
) -> None:
    try:
        language = detect_language(file)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    parser = _get_parser(language)
    try:
        ctx = parser.parse(file)
    except Exception as e:
        console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(code=1)

    if function:
        filtered = [m for m in ctx.methods if m.name == function]
        if not filtered:
            available = ", ".join(m.name for m in ctx.methods)
            console.print(
                f"[red]Error:[/red] Function '{function}' not found.\n"
                f"Available: {available}"
            )
            raise typer.Exit(code=1)
        ctx.methods = filtered

    if dry_run:
        console.print(f"[bold]Language:[/bold] {ctx.language}")
        console.print(f"[bold]Class:[/bold] {ctx.class_name or '(none)'}")
        console.print(f"[bold]Methods ({len(ctx.methods)}):[/bold]")
        for m in ctx.methods:
            params = ", ".join(f"{n}: {t}" if t else n for n, t in m.params)
            console.print(f"  {m.name}({params}) -> {m.return_type or 'None'}")
        return

    system_prompt, user_prompt = build_prompt(ctx)

    collected: list = []
    model_label = "Claude Haiku" if fast else "Claude Sonnet"
    with console.status(f"[bold green]Generating tests with {model_label}...[/bold green]"):
        try:
            for chunk in stream_tests(system_prompt, user_prompt, fast=fast):
                collected.append(chunk)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    raw_response = "".join(collected)

    try:
        out_path = write_output(raw_response, file, language, output_dir=output)
    except Exception as e:
        console.print(f"[red]Output error:[/red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✓[/bold green] Tests written to [cyan]{out_path}[/cyan]")
