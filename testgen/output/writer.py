from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def write_output(
    raw_response: str,
    source_file: str,
    language: str,
    output_dir: Optional[str] = None,
) -> str:
    code = _extract_code_block(raw_response, language)
    strategy = _extract_strategy(raw_response)

    source_path = Path(source_file)
    stem = source_path.stem

    if language == "python":
        test_filename = f"test_{stem}.py"
    else:
        test_filename = f"{stem}Test.java"

    base_dir = Path(output_dir) if output_dir else source_path.parent
    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = base_dir / test_filename

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)

    if strategy:
        console.print(
            Panel(
                strategy.strip(),
                title="[bold cyan]Test Strategy[/bold cyan]",
                border_style="cyan",
            )
        )

    return str(out_path)


def _extract_code_block(response: str, language: str) -> str:
    pattern = re.compile(
        rf"```(?:{language})?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(response)
    if match:
        return match.group(1).strip()
    return response.strip()


def _extract_strategy(response: str) -> str:
    match = re.search(r"##\s+Test Strategy(.+?)(?=##|\Z)", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
