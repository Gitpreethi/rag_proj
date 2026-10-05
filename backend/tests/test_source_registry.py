from sources.registry import SourceRegistry


def test_registry_loads_all_sources():
    registry = SourceRegistry()
    sources = registry.list_sources(enabled_only=False)
    assert len(sources) >= 15
    ids = {s.source_id for s in sources}
    assert "ncs_earthquake_archive" in ids
    assert "nidm_earthquake_guidelines" in ids


def test_get_unknown_source_raises():
    registry = SourceRegistry()
    try:
        registry.get("does_not_exist")
        raised = False
    except KeyError:
        raised = True
    assert raised
