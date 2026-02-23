def test_registry_records_event(registry, record):
    registry.record_resurrection_event(record.dna, "TEST")

    events = registry.get_events(record.dna)
    assert events[-1]["event"] == "TEST"
