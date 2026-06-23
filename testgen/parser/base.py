from abc import ABC, abstractmethod
from testgen.models import ParsedContext


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ParsedContext:
        ...
