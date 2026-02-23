def test_dashboard_includes_oversight_events(snapshot):
    assert hasattr(snapshot, "oversight_events")
    assert isinstance(snapshot.oversight_events, tuple)


def test_oversight_events_are_read_only(snapshot):
    events = snapshot.oversight_events
    assert isinstance(events, tuple)


def test_empty_oversight_is_safe(snapshot):
    assert snapshot.oversight_events == ()
