from __future__ import annotations


class ReadOnlyBrokerError(RuntimeError):
    pass


class ReadOnlyBrokerAdapter:
    """
    Read-only adapter for live broker access.

    Any trading action is strictly forbidden.
    """

    def get_positions(self):
        return []

    def get_fills(self):
        return []

    def get_pnl(self):
        return 0.0

    # ------------------------------------------------------------------
    # Forbidden operations
    # ------------------------------------------------------------------

    def place_order(self, *args, **kwargs):
        raise ReadOnlyBrokerError("Live trading is read-only in this context")

    def modify_order(self, *args, **kwargs):
        raise ReadOnlyBrokerError("Live trading is read-only in this context")

    def cancel_order(self, *args, **kwargs):
        raise ReadOnlyBrokerError("Live trading is read-only in this context")
