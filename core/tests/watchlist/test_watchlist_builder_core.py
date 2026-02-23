from pathlib import Path
from core.watchlist.builder import build_and_persist_watchlist
from core.screening.models import ScreeningResult


def test_builder_end_to_end(tmp_path: Path):
    results = [ScreeningResult("A", True, [], 0.7)]
    out = tmp_path / "wl.json"

    snap = build_and_persist_watchlist(results, "v1", out)

    assert out.exists()
    assert snap.entries[0].symbol == "A"
