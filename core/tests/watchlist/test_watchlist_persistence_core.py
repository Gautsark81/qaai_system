from pathlib import Path
from core.watchlist.persistence import save_snapshot, load_snapshot
from core.watchlist.models import WatchlistSnapshot


def test_save_and_load(tmp_path: Path):
    snap = WatchlistSnapshot("v1", "now", [])
    p = tmp_path / "watchlist.json"

    save_snapshot(snap, p)
    loaded = load_snapshot(p)

    assert loaded.version == "v1"
