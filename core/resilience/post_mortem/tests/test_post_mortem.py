from core.resilience.post_mortem.builder import PostMortemBuilder


def test_post_mortem_is_deterministic():
    builder = PostMortemBuilder()

    report1 = builder.build(
        incident_id="INC-1",
        summary="System anomaly detected",
        timeline_events=[
            {"timestamp": "2026-01-02T09:05:00", "event": "Trade executed"},
            {"timestamp": "2026-01-02T09:00:00", "event": "Risk approved"},
        ],
        decisions=[
            {"decision_id": "D2", "type": "governance"},
            {"decision_id": "D1", "type": "risk"},
        ],
        takeover_events=[
            {"authority": "human", "reason": "incident"},
        ],
        evidence_refs=[
            {"ref_id": "E2"},
            {"ref_id": "E1"},
        ],
    )

    report2 = builder.build(
        incident_id="INC-1",
        summary="System anomaly detected",
        timeline_events=[
            {"timestamp": "2026-01-02T09:05:00", "event": "Trade executed"},
            {"timestamp": "2026-01-02T09:00:00", "event": "Risk approved"},
        ],
        decisions=[
            {"decision_id": "D2", "type": "governance"},
            {"decision_id": "D1", "type": "risk"},
        ],
        takeover_events=[
            {"authority": "human", "reason": "incident"},
        ],
        evidence_refs=[
            {"ref_id": "E2"},
            {"ref_id": "E1"},
        ],
    )

    assert report1 == report2


def test_post_mortem_orders_components():
    builder = PostMortemBuilder()

    report = builder.build(
        incident_id="INC-9",
        summary="Liquidity freeze",
        timeline_events=[
            {"timestamp": "2026-01-02T10:00:00"},
            {"timestamp": "2026-01-02T09:00:00"},
        ],
        decisions=[
            {"decision_id": "D9"},
            {"decision_id": "D1"},
        ],
        takeover_events=[
            {"authority": "system"},
            {"authority": "human"},
        ],
        evidence_refs=[
            {"ref_id": "Z"},
            {"ref_id": "A"},
        ],
    )

    assert report.timeline[0]["timestamp"] == "2026-01-02T09:00:00"
    assert report.decisions[0]["decision_id"] == "D1"
    assert report.evidence_refs[0]["ref_id"] == "A"
