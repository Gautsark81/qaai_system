import pandas as pd
import pytz
from datetime import datetime
from streamlit_app.utils import export_helpers
from streamlit_app.utils.export_helpers import safe_to_ist


def test_sanitize_and_export(tmp_path):
    tz_now = datetime.now(pytz.UTC)
    df = pd.DataFrame({"ts_tz": [tz_now, tz_now], "val": [1, 2]})

    file_path = tmp_path / "test_export.xlsx"
    export_helpers.export_df_to_excel(df, file_path, index=False, sheet_name="data")

    assert file_path.exists()

    # Read back and verify timestamp is tz-naive (Excel safe)
    out = pd.read_excel(file_path)
    assert "ts_tz" in out.columns
    assert pd.api.types.is_datetime64_any_dtype(out["ts_tz"])

    # ✅ Modernized tz-check (avoid deprecated is_datetime64tz_dtype)
    assert not isinstance(out["ts_tz"].dtype, pd.DatetimeTZDtype)


def test_safe_to_ist_naive_and_aware():
    s1 = pd.Series([pd.Timestamp("2020-01-01T00:00:00")])  # naive
    out1 = safe_to_ist(s1)
    assert out1.dtype.kind in ("M",)  # datetime
    # tz-aware
    s2 = pd.Series([pd.Timestamp("2020-01-01T00:00:00", tz="UTC")])
    out2 = safe_to_ist(s2)
    assert out2.iloc[0].hour in range(0, 24)
