from core.watchlist.persistence import save_snapshot, load_snapshot
from core.watchlist.models import WatchlistSnapshot


def test_save_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "core.watchlist.persistence.WATCHLIST_PATH",
        tmp_path / "w.json",
    )

    snap = WatchlistSnapshot([], "now", "screening")
    save_snapshot(snap)
    loaded = load_snapshot()

    assert loaded.source == "screening"
