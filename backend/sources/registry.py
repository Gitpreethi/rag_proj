import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from config.settings import get_settings


class SourceDefinition(BaseModel):
    source_id: str
    name: str
    authority: str
    type: str
    format: list[str] = Field(default_factory=list)
    url: str = ""
    download_method: str = "manual"
    adapter: str = ""
    requires_authentication: bool = False
    requires_api_key: bool = False
    requires_permission: bool = False
    update_frequency: str = ""
    license_notes: str = ""
    enabled: bool = True
    local_storage: str = ""


class SourceRegistry:
    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.path = path or settings.source_registry_path
        self._sources: dict[str, SourceDefinition] = {}
        self.reload()

    def reload(self) -> None:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self._sources = {item["source_id"]: SourceDefinition(**item) for item in raw}

    def list_sources(self, enabled_only: bool = True) -> list[SourceDefinition]:
        items = list(self._sources.values())
        if enabled_only:
            items = [s for s in items if s.enabled]
        return sorted(items, key=lambda s: s.source_id)

    def get(self, source_id: str) -> SourceDefinition:
        if source_id not in self._sources:
            raise KeyError(f"Unknown source_id: {source_id}")
        return self._sources[source_id]

    def to_public_dict(self, source: SourceDefinition) -> dict[str, Any]:
        return source.model_dump()
