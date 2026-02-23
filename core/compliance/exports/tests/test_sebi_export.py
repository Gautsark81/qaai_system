from core.compliance.exports.exporter import SEBIAuditExporter


def test_sebi_export_is_deterministic():
    exporter = SEBIAuditExporter()

    trades = [
        {"trade_id": "T2", "symbol": "INFY"},
        {"trade_id": "T1", "symbol": "RELIANCE"},
    ]
    decisions = [
        {"decision_id": "D2", "type": "governance"},
        {"decision_id": "D1", "type": "risk"},
    ]
    explanations = [
        "Trade executed after risk approval.",
        "Risk approved by system.",
    ]

    export1 = exporter.build(
        trades=trades,
        decisions=decisions,
        explanations=explanations,
    )
    export2 = exporter.build(
        trades=trades,
        decisions=decisions,
        explanations=explanations,
    )

    assert export1.export_id == export2.export_id
    assert export1.trades == export2.trades
    assert export1.decisions == export2.decisions
    assert export1.explanations == export2.explanations


def test_export_changes_when_content_changes():
    exporter = SEBIAuditExporter()

    export1 = exporter.build(
        trades=[{"trade_id": "T1"}],
        decisions=[],
        explanations=[],
    )
    export2 = exporter.build(
        trades=[{"trade_id": "T2"}],
        decisions=[],
        explanations=[],
    )

    assert export1.export_id != export2.export_id
