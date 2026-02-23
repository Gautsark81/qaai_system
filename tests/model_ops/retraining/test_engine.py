from datetime import datetime

from qaai_system.model_ops.retraining import (
    RetrainingDecisionEngine,
    RetrainingSignals,
    MarketRegime,
)


class DummyAuditSink:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def dummy_regime_classifier(_):
    return MarketRegime.HIGH_VOL


def test_retraining_triggered_on_decay():
    engine = RetrainingDecisionEngine(
        regime_classifier=dummy_regime_classifier,
        audit_sink=DummyAuditSink(),
        clock=DummyClock(),
    )

    signals = RetrainingSignals(
        decay_detected=True,
        decay_reasons=["SharpeDecay"],
        shadow_divergence=0.1,
        feature_drift_psi=0.1,
    )

    decision, plan = engine.evaluate(
        model_id="m1",
        signals=signals,
        market_snapshot={},
    )

    assert decision.should_retrain is True
    assert plan is not None
    assert plan.regime == MarketRegime.HIGH_VOL
