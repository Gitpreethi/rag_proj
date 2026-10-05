from pathlib import Path

from config.settings import get_settings
from sources.adapters.generic_document import GenericDocumentAdapter
from sources.adapters.historical_cases import HistoricalCasesAdapter
from sources.adapters.ncs import NCSAdapter
from sources.registry import SourceDefinition, SourceRegistry


def get_adapter(source: SourceDefinition):
    settings = get_settings()
    raw_root = settings.raw_data_root
    mapping = {
        "ncs": NCSAdapter,
        "historical_reports": HistoricalCasesAdapter,
    }
    cls = mapping.get(source.adapter, GenericDocumentAdapter)
    return cls(source, raw_root)


def resolve_manual_directory(source_id: str) -> Path:
    settings = get_settings()
    registry = SourceRegistry()
    source = registry.get(source_id)
    base = settings.raw_data_root / source_id
    if not base.exists():
        alt = settings.raw_data_root / source.adapter if source.adapter else base
        return alt if alt.exists() else base
    return base
