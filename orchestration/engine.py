from datetime import datetime

from .audit import DryRunAuditEvent


class DryRunOrchestrator:
    """
    Executes full trading pipeline in dry-run mode.
    """

    def __init__(
        self,
        *,
        strategy_engine,
        execution_engine,
        broker,
        audit_sink,
        clock,
    ):
        self.strategy_engine = strategy_engine
        self.execution_engine = execution_engine
        self.broker = broker
        self.audit_sink = audit_sink
        self.clock = clock

    def on_market_event(self, *, model_id: str, market_event):
        # 1️⃣ Generate signal
        signal = self.strategy_engine.generate(market_event)

        # 2️⃣ Create order (still virtual)
        order = self.execution_engine.create_order(
            model_id=model_id,
            signal=signal,
        )

        # 3️⃣ Drop at broker boundary
        result = self.broker.submit_order(order)

        # 4️⃣ Audit
        self.audit_sink.emit(
            DryRunAuditEvent(
                model_id=model_id,
                action="order_dropped",
                payload={
                    "signal": signal,
                    "order": order,
                    "result": result,
                },
                timestamp=self.clock.utcnow(),
            )
        )

        return result
