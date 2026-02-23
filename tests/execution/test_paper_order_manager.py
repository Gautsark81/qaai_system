from execution.order_manager.paper import PaperOrderManager
from execution.execution_journal import ExecutionJournal
import tempfile
import os


class DummyProvider:
    def __init__(self):
        self._orders = {}


def test_paper_order_idempotent_submit():
    with tempfile.TemporaryDirectory() as d:
        journal = ExecutionJournal(os.path.join(d, "journal.jsonl"))
        provider = DummyProvider()
        mgr = PaperOrderManager(provider, journal)

        order = {"symbol": "SBIN", "qty": 1}

        r1 = mgr.submit(order)
        r2 = mgr.submit(order | {"order_id": r1["order_id"]})

        assert r1["order_id"] == r2["order_id"]
        assert r2["status"] == "DUPLICATE"
