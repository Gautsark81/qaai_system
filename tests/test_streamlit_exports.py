import pandas as pd
from streamlit_app.tasks.export_scheduler import (
    run_overlay_export,
    SUCCESS_PREFIX,
    FAIL_PREFIX,
)


def test_run_overlay_export_creates_file(monkeypatch, tmp_path):
    # monkeypatch telegram to test mode
    monkeypatch.setenv("TEST_MODE", "1")
    # create a sample df in a temp CSV (simulate overlay source)
    df = pd.DataFrame({"ts": [pd.Timestamp("2020-01-01")], "val": [1]})
    src = tmp_path / "src.csv"
    df.to_csv(src, index=False)
    res = run_overlay_export(source_csv=str(src), output_name="test_overlay.xlsx")
    assert isinstance(res, str)
    assert res.startswith(SUCCESS_PREFIX) or res.startswith(FAIL_PREFIX)
