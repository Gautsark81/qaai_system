from datetime import datetime

from qaai_system.model_ops.decay_detection import (
    LiveDecayDetectionEngine,
    LiveDecayMetrics,
    SharpeDecayDetector,
)


class DummyAuditSink:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def test_engine_emits_decay_event():
    engine = LiveDecayDetectionEngine(
        detectors=[SharpeDecayDetector(drop_ratio=0.8)],
        audit_sink=DummyAuditSink(),
        clock=DummyClock(),
    )

    metrics = LiveDecayMetrics(
        sharpe=1.0,
        rolling_sharpe=0.5,
        max_drawdown=0.1,
        volatility=0.2,
        prediction_entropy=0.3,
        psi=0.05,
        shadow_disagreement_rate=0.05,
    )

    decision = engine.evaluate(model_id="m1", metrics=metrics)

    assert decision.decaying is True
    assert "SharpeDecayDetector" in decision.reasons
