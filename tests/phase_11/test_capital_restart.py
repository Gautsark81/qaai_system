from pathlib import Path
import tempfile

from modules.capital.ledger import CapitalLedger


def test_restart_replays_exact_state():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ledger.jsonl"

        ledger = CapitalLedger(path)
        ledger.initialize(1000)
        ledger.reserve(200)
        ledger.allocate("s1", 300)

        restarted = CapitalLedger(path)

        assert restarted.total_capital == 1000
        assert restarted.reserved_capital == 200
        assert restarted.allocation_for("s1") == 300
        assert restarted.free_capital == 500
