from modules.capital.attribution import CapitalAttributionEngine


def test_neutral_attribution_when_no_scaling():
    report = CapitalAttributionEngine.explain(
        requested_notional=100_000,
        signals={
            "DD": (1.0, "No drawdown"),
            "VOL": (1.0, "Low vol"),
            "REGIME": (1.0, "Calm"),
        },
    )

    assert report.final_scale == 1.0
    assert report.dominant_signal == "NONE"
    assert all(c.contribution_pct == 0.0 for c in report.contributions)


def test_attribution_identifies_dominant_signal():
    report = CapitalAttributionEngine.explain(
        requested_notional=100_000,
        signals={
            "DD": (0.50, "High drawdown"),
            "VOL": (0.80, "Elevated vol"),
            "REGIME": (0.90, "Choppy"),
        },
    )

    assert report.final_scale == 0.5 * 0.8 * 0.9
    assert report.final_notional == 100_000 * report.final_scale
    assert report.dominant_signal == "DD"

    # Contributions sum to ~1
    total = sum(c.contribution_pct for c in report.contributions)
    assert round(total, 6) == 1.0


def test_attribution_is_scale_down_only():
    report = CapitalAttributionEngine.explain(
        requested_notional=50_000,
        signals={
            "DD": (1.2, "Illegal up-scale"),   # should be clamped
            "VOL": (0.7, "Vol spike"),
        },
    )

    assert report.final_scale <= 1.0
    assert report.final_notional <= 50_000
