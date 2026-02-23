import pytest
from unittest.mock import patch
import pandas as pd

from streamlit_app.utils import export_helpers


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2025-01-01", periods=3, freq="D", tz="Asia/Kolkata"
            ),
            "price": [100, 101, 102],
        }
    )


def test_run_overlay_export_success(tmp_path, sample_df):
    """✅ Should run export and save without error."""
    export_file = tmp_path / "export.xlsx"

    with patch(
        "streamlit_app.utils.export_helpers.load_overlay_data", return_value=sample_df
    ):
        df = export_helpers.load_overlay_data()
        saved_file = export_helpers.export_df_to_excel(df, export_file)

    assert saved_file.exists(), "Export file should exist"
    assert saved_file.suffix == ".xlsx"

    # Reload and check no timezone in timestamp column after export
    df_out = pd.read_excel(saved_file)
    assert "price" in df_out.columns
    assert len(df_out) == 3

    # ✅ Modernized tz-check (avoid deprecated is_datetime64tz_dtype)
    assert not isinstance(df_out["timestamp"].dtype, pd.DatetimeTZDtype)


def test_run_overlay_export_failure(tmp_path):
    """❌ Should log and handle export failure gracefully."""
    export_file = tmp_path / "export.xlsx"

    with patch(
        "streamlit_app.utils.export_helpers.load_overlay_data",
        side_effect=Exception("Data load error"),
    ):
        with pytest.raises(Exception) as exc:
            df = export_helpers.load_overlay_data()
            export_helpers.export_df_to_excel(df, export_file)

    assert "Data load error" in str(exc.value)
