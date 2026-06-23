from __future__ import annotations

import re
import warnings
from typing import List, Tuple

from testgen.models import MethodInfo, ParsedContext
from testgen.parser.base import BaseParser

try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False


class JavaParser(BaseParser):
    def parse(self, file_path: str) -> ParsedContext:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        if JAVALANG_AVAILABLE:
            try:
                return self._parse_with_javalang(file_path, source)
            except Exception as e:
                warnings.warn(f"javalang parsing failed ({e}); falling back to regex extractor.")

        return self._parse_with_regex(file_path, source)

    def _parse_with_javalang(self, file_path: str, source: str) -> ParsedContext:
        import javalang
        tree = javalang.parse.parse(source)

        class_name = ""
        imports = [imp.path for imp in tree.imports]
        methods: List[MethodInfo] = []

        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            if not class_name:
                class_name = node.name
            for method in node.methods:
                if "public" not in (method.modifiers or set()):
                    continue
                params = [
                    (p.name, p.type.name if hasattr(p.type, "name") else str(p.type))
                    for p in (method.parameters or [])
                ]
                raw_throws = method.throws or []
                throws = [
                    t if isinstance(t, str) else t.name
                    for t in raw_throws
                ]
                annotations = [a.name for a in (method.annotations or [])]
                return_type = (
                    method.return_type.name
                    if method.return_type and hasattr(method.return_type, "name")
                    else "void"
                )
                methods.append(
                    MethodInfo(
                        name=method.name,
                        params=params,
                        return_type=return_type,
                        docstring="",
                        throws=throws,
                        annotations=annotations,
                    )
                )

        return ParsedContext(
            language="java",
            file_path=file_path,
            class_name=class_name,
            imports=imports,
            methods=methods,
            raw_source=source,
        )

    def _parse_with_regex(self, file_path: str, source: str) -> ParsedContext:
        class_match = re.search(r"class\s+(\w+)", source)
        class_name = class_match.group(1) if class_match else ""

        import_pattern = re.compile(r"import\s+([\w.]+);")
        imports = import_pattern.findall(source)

        method_pattern = re.compile(
            r"public\s+(?:static\s+)?(\w[\w<>,\s]*?)\s+(\w+)\s*\(([^)]*)\)"
        )
        methods: List[MethodInfo] = []
        for match in method_pattern.finditer(source):
            return_type = match.group(1).strip()
            method_name = match.group(2).strip()
            raw_params = match.group(3).strip()
            params: List[Tuple[str, str]] = []
            if raw_params:
                for part in raw_params.split(","):
                    parts = part.strip().split()
                    if len(parts) >= 2:
                        params.append((parts[-1], " ".join(parts[:-1])))
            methods.append(
                MethodInfo(
                    name=method_name,
                    params=params,
                    return_type=return_type,
                    docstring="",
                )
            )

        return ParsedContext(
            language="java",
            file_path=file_path,
            class_name=class_name,
            imports=imports,
            methods=methods,
            raw_source=source,
        )
