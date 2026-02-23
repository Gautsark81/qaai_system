from datetime import datetime

from core.evidence.report_builder import build_audit_report
from core.evidence.replay_contracts import ReplayFrame


def make_frame(ts):
    return ReplayFrame(
        timestamp=ts,
        capital_allocations={"a": 1.0},
        governance_states={},
        market_regime="TREND",
        regime_confidence=0.9,
    )


def test_build_audit_report_produces_checksum():
    frames = [
        make_frame(datetime(2024, 1, 1)),
        make_frame(datetime(2024, 1, 2)),
    ]

    report = build_audit_report(frames=frames)

    assert report.checksum
    assert report.evidence_count == 2
