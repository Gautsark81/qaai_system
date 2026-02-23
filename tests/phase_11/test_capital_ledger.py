from pathlib import Path
import tempfile

from modules.capital.ledger import CapitalLedger


def test_basic_reserve_and_release():
    with tempfile.TemporaryDirectory() as d:
        ledger = CapitalLedger(Path(d) / "ledger.jsonl")
        ledger.initialize(1000)

        ledger.reserve(300)
        assert ledger.reserved_capital == 300
        assert ledger.free_capital == 700

        ledger.release(200)
        assert ledger.reserved_capital == 100
        assert ledger.free_capital == 900


def test_allocation_and_deallocation():
    with tempfile.TemporaryDirectory() as d:
        ledger = CapitalLedger(Path(d) / "ledger.jsonl")
        ledger.initialize(1000)

        ledger.allocate("s1", 400)
        assert ledger.allocation_for("s1") == 400
        assert ledger.free_capital == 600

        ledger.deallocate("s1", 400)
        assert ledger.free_capital == 1000
