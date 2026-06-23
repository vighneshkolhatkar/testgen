from __future__ import annotations

import ast
from typing import Union

from testgen.models import MethodInfo, ParsedContext
from testgen.parser.base import BaseParser


class PythonParser(BaseParser):
    def parse(self, file_path: str) -> ParsedContext:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=file_path)
        imports = self._extract_imports(tree)
        methods = []
        class_name = ""

        # Walk top-level body nodes only to preserve order.
        # For class_name selection: prefer the first class that has methods
        # (skips data-only classes like @dataclass with no methods).
        first_class: str = ""
        first_class_with_methods: str = ""

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if not first_class:
                    first_class = node.name
                class_methods = [
                    item for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if class_methods and not first_class_with_methods:
                    first_class_with_methods = node.name
                for item in class_methods:
                    methods.append(self._extract_method(item))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_method(node))

        class_name = first_class_with_methods or first_class

        # deduplicate while preserving order
        seen = set()
        unique_methods = []
        for m in methods:
            if m.name not in seen:
                seen.add(m.name)
                unique_methods.append(m)

        return ParsedContext(
            language="python",
            file_path=file_path,
            class_name=class_name,
            imports=imports,
            methods=unique_methods,
            raw_source=source,
        )

    def _extract_method(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> MethodInfo:
        params = []
        for arg in node.args.args:
            if arg.arg == "self":
                continue
            type_hint = ast.unparse(arg.annotation) if arg.annotation else ""
            params.append((arg.arg, type_hint))

        return_type = ast.unparse(node.returns) if node.returns else ""
        docstring = ast.get_docstring(node) or ""
        is_async = isinstance(node, ast.AsyncFunctionDef)

        return MethodInfo(
            name=node.name,
            params=params,
            return_type=return_type,
            docstring=docstring,
            is_async=is_async,
        )

    def _extract_imports(self, tree: ast.AST) -> list:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
