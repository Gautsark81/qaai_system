import pandas as pd
from streamlit_app.utils.export_helpers import safe_to_ist, export_df_to_excel


def test_safe_to_ist_aware():
    import pytz

    tz = pytz.UTC
    s = pd.Series([pd.Timestamp("2020-01-01T00:00:00", tz=tz)])
    out = safe_to_ist(s)
    assert out.dtype == "datetime64[ns]" or out.isna().sum() == 0


def test_export_atomic_tmpfile(tmp_path):
    df = pd.DataFrame({"a": [1]})
    out = tmp_path / "out.xlsx"
    ret = export_df_to_excel(df, out)
    assert ret.exists()
    assert ret == out.resolve()
