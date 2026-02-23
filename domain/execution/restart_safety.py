from domain.execution.execution_ledger import ExecutionLedger


class RestartSafety:
    """
    Ensures system restart cannot duplicate execution.
    """

    @staticmethod
    def safe_to_start(ledger: ExecutionLedger) -> bool:
        # Placeholder invariant: ledger must exist & be loadable
        return ledger is not None
