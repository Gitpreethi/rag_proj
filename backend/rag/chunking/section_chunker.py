import re
from dataclasses import dataclass

import tiktoken

from config.settings import get_settings


@dataclass
class TextChunk:
    text: str
    section: str = ""
    subsection: str = ""
    page: str = ""
    token_count: int = 0


class SectionAwareChunker:
    HEADING_RE = re.compile(r"^(?:\d+(\.\d+)*\s+)?[A-Z][A-Za-z0-9 \-/]{3,}$")

    def __init__(self) -> None:
        settings = get_settings()
        self.chunk_size = settings.chunk_size_tokens
        self.overlap = settings.chunk_overlap_tokens
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoder = None

    def count_tokens(self, text: str) -> int:
        if self.encoder:
            return len(self.encoder.encode(text))
        return max(1, len(text.split()))

    def split(self, text: str) -> list[TextChunk]:
        sections = self._split_sections(text)
        chunks: list[TextChunk] = []
        for section, subsection, body in sections:
            chunks.extend(self._chunk_body(body, section, subsection))
        return chunks

    def _split_sections(self, text: str) -> list[tuple[str, str, str]]:
        lines = [ln.strip() for ln in text.splitlines()]
        current_section = ""
        current_sub = ""
        buffer: list[str] = []
        output: list[tuple[str, str, str]] = []

        def flush():
            if buffer:
                output.append((current_section, current_sub, "\n".join(buffer).strip()))

        for line in lines:
            if not line:
                buffer.append("")
                continue
            if self.HEADING_RE.match(line):
                flush()
                buffer = []
                if not current_section:
                    current_section = line
                else:
                    current_sub = line
                continue
            buffer.append(line)
        flush()
        if not output and text.strip():
            output.append(("", "", text.strip()))
        return output

    def _chunk_body(self, body: str, section: str, subsection: str) -> list[TextChunk]:
        words = body.split()
        if not words:
            return []
        chunks: list[TextChunk] = []
        start = 0
        while start < len(words):
            end = start
            piece: list[str] = []
            while end < len(words):
                piece = words[start : end + 1]
                if self.count_tokens(" ".join(piece)) > self.chunk_size:
                    break
                end += 1
            if end == start:
                end += 1
                piece = words[start:end]
            text = " ".join(piece).strip()
            chunks.append(
                TextChunk(
                    text=text,
                    section=section,
                    subsection=subsection,
                    token_count=self.count_tokens(text),
                )
            )
            if end >= len(words):
                break
            start = max(end - self.overlap, start + 1)
        return chunks
