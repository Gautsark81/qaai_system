import os
import tempfile
from execution.paper_store import PaperTradeStore


def test_atomic_append_and_replay():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "trades.jsonl")
        store = PaperTradeStore(path)

        trades = [
            {"id": 1, "pnl": 10},
            {"id": 2, "pnl": -5},
        ]

        for t in trades:
            store.append(t)

        replayed = list(store.replay())
        assert replayed == trades


def test_replay_empty_if_missing():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "missing.jsonl")
        store = PaperTradeStore(path)

        assert list(store.replay()) == []


def test_no_partial_write_visible():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "trades.jsonl")
        store = PaperTradeStore(path)

        store.append({"id": 1})

        assert os.path.exists(path)
        assert not os.path.exists(path + ".tmp")
