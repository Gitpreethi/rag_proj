from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sources.registry import SourceDefinition


@dataclass
class DownloadResult:
    success: bool
    message: str
    files: list[Path] = field(default_factory=list)
    skipped: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    success: bool
    message: str
    records_written: int = 0
    errors: list[str] = field(default_factory=list)


class SourceAdapter(ABC):
    def __init__(self, source: SourceDefinition, raw_root: Path) -> None:
        self.source = source
        self.raw_root = raw_root

    def dated_raw_dir(self) -> Path:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = self.raw_root / self.source.source_id / day
        path.mkdir(parents=True, exist_ok=True)
        return path

    @abstractmethod
    def download(self) -> DownloadResult:
        """Mode A/C: attempt automatic or URL-triggered download."""

    @abstractmethod
    def ingest_manual_files(self, directory: Path) -> ParseResult:
        """Mode B: process files placed under data/raw/."""

    @abstractmethod
    def parse_and_normalize(self, raw_files: list[Path]) -> ParseResult:
        """Parse raw files into structured DB / document registry."""
