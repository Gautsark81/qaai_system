from domain.behavior_fingerprint.execution_behavior import ExecutionStyleFingerprint


def test_execution_style_fingerprint():
    fp = ExecutionStyleFingerprint(
        order_types={"market", "limit"},
        slippage_sensitivity="medium",
        latency_tolerance_ms=500,
        partial_fill_handling="retry",
    )

    assert "market" in fp.order_types
    assert fp.latency_tolerance_ms > 0
