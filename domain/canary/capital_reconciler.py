from domain.canary.authorized_trade_record import AuthorizedTradeRecord
from domain.broker.broker_trade_snapshot import BrokerTradeSnapshot
from domain.canary.reconciliation_result import ReconciliationResult


class CapitalReconciler:
    """
    Compares authorized vs broker-executed capital.
    """

    @staticmethod
    def reconcile(
        authorized: AuthorizedTradeRecord,
        broker: BrokerTradeSnapshot,
        tolerance_pct: float = 0.01,   # 1%
    ) -> ReconciliationResult:

        delta = broker.executed_value - authorized.authorized_capital
        tolerance = authorized.authorized_capital * tolerance_pct

        within = abs(delta) <= tolerance

        return ReconciliationResult(
            intent_id=authorized.intent_id,
            authorized_capital=authorized.authorized_capital,
            broker_executed_capital=broker.executed_value,
            delta=delta,
            within_tolerance=within,
        )
