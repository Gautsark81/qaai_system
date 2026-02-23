# File: tests/dashboard/test_roadmap_registry.py

def test_roadmap_registry_exists():
    from core.dashboard.roadmap import get_full_roadmap
    roadmap = get_full_roadmap()
    assert isinstance(roadmap, list)
    assert len(roadmap) > 0


def test_all_phases_have_unique_ids():
    from core.dashboard.roadmap import get_full_roadmap
    ids = [p["phase_id"] for p in get_full_roadmap()]
    assert len(ids) == len(set(ids))


def test_phase_ordering_is_strict():
    from core.dashboard.roadmap import get_full_roadmap
    orders = [p["order"] for p in get_full_roadmap()]
    assert orders == sorted(orders)
