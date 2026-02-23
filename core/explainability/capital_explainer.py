from core.capital.usage_ledger.ledger import CapitalUsageLedger


class CapitalExplainer:
    """
    Explains capital state using Phase 24.1 ledger.
    """

    def explain(self, ledger: CapitalUsageLedger) -> str:
        lines = ["Capital Explanation:"]

        for strategy in {e.strategy_id for e in ledger.entries()}:
            allocation = 0.0
            consumption = 0.0
            release = 0.0

            for e in ledger.entries():
                if e.strategy_id != strategy:
                    continue
                if e.event_type.value == "allocation":
                    allocation += e.amount
                elif e.event_type.value == "consumption":
                    consumption += e.amount
                elif e.event_type.value == "release":
                    release += e.amount

            used = ledger.used_capital_by_strategy(strategy)

            lines.append(
                f"Strategy {strategy}: "
                f"Allocated: {int(allocation)}, "
                f"Consumed: {int(consumption)}, "
                f"Released: {int(release)}, "
                f"Used Capital: {int(used)}"
            )

        return "\n".join(lines)
