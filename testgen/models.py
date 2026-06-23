from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class MethodInfo:
    name: str
    params: List[Tuple[str, str]]
    return_type: str
    docstring: str
    is_async: bool = False
    throws: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)


@dataclass
class ParsedContext:
    language: str
    file_path: str
    class_name: str
    imports: List[str]
    methods: List[MethodInfo]
    raw_source: str
