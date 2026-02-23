from pathlib import Path
from typing import TextIO


class StreamHandler:
    def __init__(self, stream: TextIO):
        self.stream = stream

    def emit(self, line: str) -> None:
        self.stream.write(line + "\n")
        self.stream.flush()


class JsonlFileHandler:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
