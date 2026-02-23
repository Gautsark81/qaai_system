import json
from pathlib import Path

from qaai_system.analytics.metrics.cycle_metrics import (
    record_cycle_metrics,
    DEFAULT_METRICS_PATH,
)


def _read_single_json_line(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    assert text, "metrics file should not be empty"
    first_line = text.splitlines()[0]
    return json.loads(first_line)


def test_record_cycle_metrics_writes_json_line(tmp_path: Path) -> None:
    store = tmp_path / "cycle_metrics.jsonl"

    record_cycle_metrics(
        {
            "mode": "paper",
            "num_orders": 3,
            "num_signals": 7,
        },
        store_path=store,
    )

    assert store.exists(), "metrics file should be created"
    data = _read_single_json_line(store)

    # Standard fields
    assert data["event"] == "TRADING_CYCLE"
    assert "ts" in data

    # Custom fields
    assert data["mode"] == "paper"
    assert data["num_orders"] == 3
    assert data["num_signals"] == 7


def test_record_cycle_metrics_sanitises_non_jsonable_values(tmp_path: Path) -> None:
    store = tmp_path / "cycle_metrics.jsonl"

    class Dummy:
        def __repr__(self) -> str:
            return "<Dummy-object>"

    record_cycle_metrics(
        {
            "mode": "paper",
            "obj": Dummy(),
        },
        store_path=store,
    )

    data = _read_single_json_line(store)

    # Non-JSON-able value must be converted to string
    assert isinstance(data["obj"], str)
    assert "<Dummy-object>" in data["obj"]


def test_record_cycle_metrics_fail_soft_on_bad_directory(
    tmp_path: Path, monkeypatch
) -> None:
    from qaai_system.analytics.metrics import cycle_metrics as cm

    def boom(_path: Path) -> None:
        raise OSError("boom")

    monkeypatch.setattr(cm, "_ensure_parent_dir", boom)

    # Must not raise even if directory creation fails
    record_cycle_metrics({"mode": "paper"}, store_path=tmp_path / "ignored.jsonl")


def test_default_metrics_path_constant_is_a_logs_file() -> None:
    assert isinstance(DEFAULT_METRICS_PATH, Path)
    path_str = str(DEFAULT_METRICS_PATH).replace("\\", "/")
    assert "logs" in path_str
    assert DEFAULT_METRICS_PATH.name.endswith(".jsonl")
