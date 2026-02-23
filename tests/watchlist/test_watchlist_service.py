from screening.results import ScreeningResult
from watchlist.service import WatchlistService


def test_watchlist_add_remove_set_and_persistence(tmp_path):
    base_dir = tmp_path / "watchlists"
    svc = WatchlistService(base_dir=str(base_dir))

    # add
    svc.add("DAY_SCALP", ["NIFTY", "BANKNIFTY"])
    assert set(svc.get("DAY_SCALP")) == {"BANKNIFTY", "NIFTY"}

    # remove
    svc.remove("DAY_SCALP", ["BANKNIFTY"])
    assert set(svc.get("DAY_SCALP")) == {"NIFTY"}

    # set (replace)
    svc.set("DAY_SCALP", ["FINNIFTY"])
    assert svc.get("DAY_SCALP") == ["FINNIFTY"]

    # persistence: new instance with same base_dir should see same data
    svc2 = WatchlistService(base_dir=str(base_dir))
    assert svc2.get("DAY_SCALP") == ["FINNIFTY"]


def test_watchlist_update_from_screen(tmp_path):
    base_dir = tmp_path / "watchlists"
    svc = WatchlistService(base_dir=str(base_dir))

    # fake screening results
    results = [
        ScreeningResult(symbol="NIFTY", score=1.0),
        ScreeningResult(symbol="BANKNIFTY", score=0.5),
    ]

    svc.update_from_screen("INTRADAY_CORE", results)

    wl = svc.get("INTRADAY_CORE")
    assert set(wl) == {"NIFTY", "BANKNIFTY"}
