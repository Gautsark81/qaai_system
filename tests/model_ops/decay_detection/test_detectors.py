from qaai_system.model_ops.decay_detection import (
    LiveDecayMetrics,
    SharpeDecayDetector,
    DriftDetector,
    ShadowDivergenceDetector,
)


def base_metrics(**overrides):
    base = dict(
        sharpe=1.0,
        rolling_sharpe=1.0,
        max_drawdown=0.1,
        volatility=0.2,
        prediction_entropy=0.3,
        psi=0.05,
        shadow_disagreement_rate=0.05,
    )
    base.update(overrides)
    return LiveDecayMetrics(**base)


def test_sharpe_decay_detected():
    detector = SharpeDecayDetector(drop_ratio=0.7)
    assert detector.detect(base_metrics(rolling_sharpe=0.5))


def test_drift_detected():
    detector = DriftDetector(psi_limit=0.2)
    assert detector.detect(base_metrics(psi=0.3))


def test_shadow_divergence_detected():
    detector = ShadowDivergenceDetector(disagreement_limit=0.2)
    assert detector.detect(base_metrics(shadow_disagreement_rate=0.4))
