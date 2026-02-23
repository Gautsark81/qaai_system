# core/paper/paper_broker.py

class PaperBroker:
    """
    Paper broker abstraction.

    Supports explicit failure injection for STEP-9 testing.
    """

    def __init__(self, *, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def place_order(self, symbol, side, qty, price):
        # 🔒 STEP-9.5 — BROKER FAILURE HARD STOP
        if self.simulate_failure:
            raise RuntimeError("Broker unavailable")

        # Normal paper execution path
        return {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "status": "FILLED",
        }
