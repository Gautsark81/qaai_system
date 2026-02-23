import json
import os
import tempfile

from qaai_system.execution.execution_journal import ExecutionJournal


def test_append_and_replay_single_event():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "journal.jsonl")
        j = ExecutionJournal(path)

        event = {
            "type": "ORDER_CREATED",
            "order_id": "o1",
            "symbol": "NIFTY",
            "qty": 1,
        }

        j.append(event)
        replayed = list(j.replay())

        assert replayed == [event]


def test_append_and_replay_multiple_events():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "journal.jsonl")
        j = ExecutionJournal(path)

        events = [
            {"type": "ORDER_CREATED", "order_id": "o1"},
            {"type": "ORDER_FILLED", "order_id": "o1", "pnl": 10.0},
        ]

        for e in events:
            j.append(e)

        replayed = list(j.replay())
        assert replayed == events


def test_replay_ignores_partial_line():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "journal.jsonl")

        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"ok": 1}) + "\n")
            f.write('{"bad_json": ')  # truncated line

        j = ExecutionJournal(path)
        replayed = list(j.replay())

        assert replayed == [{"ok": 1}]


def test_replay_is_deterministic():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "journal.jsonl")
        j = ExecutionJournal(path)

        events = [
            {"type": "A", "x": 1},
            {"type": "B", "y": 2},
        ]

        for e in events:
            j.append(e)

        r1 = list(j.replay())
        r2 = list(j.replay())

        assert r1 == r2
        assert r1 == events


def test_double_replay_produces_same_output():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "journal.jsonl")
        j = ExecutionJournal(path)

        j.append({"type": "ORDER_CREATED", "id": "1"})
        j.append({"type": "ORDER_FILLED", "id": "1", "pnl": 5})

        first = list(j.replay())
        second = list(j.replay())

        assert first == second
