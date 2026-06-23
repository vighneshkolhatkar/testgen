from __future__ import annotations

from typing import Tuple

from testgen.models import ParsedContext


_SYSTEM_PROMPT = """\
You are an expert software engineer specializing in test-driven development.
Your task is to generate comprehensive, production-quality unit tests.

Rules:
- Generate tests that are immediately runnable — no placeholders or TODOs
- Cover the happy path, edge cases, boundary conditions, and error cases
- Use mocking for external dependencies
- Each test method must have a clear, descriptive name:
  Python: test_<method>_<scenario>
  Java: should_<scenario>_when_<condition>
- After the test code block, add a "## Test Strategy" section explaining what was covered and why
- Do not include explanatory prose inside the test code — only real, runnable code\
"""


def _format_python_prompt(ctx: ParsedContext) -> str:
    lines = [
        f"Generate pytest unit tests for the following Python {'class' if ctx.class_name else 'module'}.",
        "",
        f"File: {ctx.file_path}",
    ]
    if ctx.class_name:
        lines.append(f"Class: {ctx.class_name}")
    if ctx.imports:
        lines += ["", "Imports:", *[f"  - {imp}" for imp in ctx.imports]]

    lines += ["", "Methods to test:"]
    for m in ctx.methods:
        sig = f"{'async ' if m.is_async else ''}{m.name}("
        param_parts = [f"{n}: {t}" if t else n for n, t in m.params]
        sig += ", ".join(param_parts) + ")"
        if m.return_type:
            sig += f" -> {m.return_type}"
        lines.append(f"  {sig}")
        if m.docstring:
            lines.append(f'    """{m.docstring}"""')

    lines += [
        "",
        "Requirements:",
        "- Use pytest as the test framework",
        "- Use unittest.mock.patch and unittest.mock.MagicMock for mocking",
        "- Output a complete, self-contained test file with all necessary imports",
        "- The test file must be runnable with: pytest <filename>",
    ]
    return "\n".join(lines)


def _format_java_prompt(ctx: ParsedContext) -> str:
    lines = [
        f"Generate JUnit 5 unit tests for the following Java class.",
        "",
        f"Class: {ctx.class_name}",
        f"File: {ctx.file_path}",
    ]
    if ctx.imports:
        lines += ["", "Imports:", *[f"  - {imp}" for imp in ctx.imports[:10]]]

    lines += ["", "Public methods to test:"]
    for m in ctx.methods:
        sig = f"{m.return_type} {m.name}("
        param_parts = [f"{t} {n}" for n, t in m.params]
        sig += ", ".join(param_parts) + ")"
        if m.throws:
            sig += f" throws {', '.join(m.throws)}"
        if m.annotations:
            for ann in m.annotations:
                lines.append(f"  @{ann}")
        lines.append(f"  {sig}")

    lines += [
        "",
        "Requirements:",
        "- Use JUnit 5 (@Test, @ExtendWith(MockitoExtension.class))",
        "- Use Mockito (@Mock, @InjectMocks, when/thenReturn, verify)",
        "- Output a complete, compilable Java test class with all necessary imports",
        "- Package declaration should match the source class",
    ]
    return "\n".join(lines)


def build_prompt(ctx: ParsedContext) -> Tuple[str, str]:
    if ctx.language == "python":
        return _SYSTEM_PROMPT, _format_python_prompt(ctx)
    return _SYSTEM_PROMPT, _format_java_prompt(ctx)
