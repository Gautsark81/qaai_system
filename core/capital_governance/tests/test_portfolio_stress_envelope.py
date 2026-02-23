from core.capital.stress.stress_report import StressReport
from core.capital_governance.stress_envelope import (
    build_portfolio_stress_envelope,
)


def test_portfolio_stress_envelope_aggregation():
    reports = [
        StressReport(
            strategy_id="s1",
            worst_case_loss=1000.0,
            scenario="crash",
        ),
        StressReport(
            strategy_id="s2",
            worst_case_loss=500.0,
            scenario="liquidity_freeze",
        ),
    ]

    snapshot = build_portfolio_stress_envelope(reports)
    envelope = snapshot.stress_envelope

    assert envelope.total_worst_case_loss == 1500.0
    assert envelope.scenario_count == 2


def test_stress_envelope_is_deterministic():
    report = StressReport(
        strategy_id="s1",
        worst_case_loss=750.0,
        scenario="vol_spike",
    )

    r1 = build_portfolio_stress_envelope([report])
    r2 = build_portfolio_stress_envelope([report])

    assert r1.stress_envelope == r2.stress_envelope
