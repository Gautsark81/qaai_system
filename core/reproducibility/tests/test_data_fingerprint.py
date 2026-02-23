import tempfile
from pathlib import Path
from core.reproducibility.data_fingerprint import DataFingerprint


def test_data_fingerprint_file_hash_stable():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"sample_data")
        tmp_path = Path(tmp.name)

    fp1 = DataFingerprint.from_file(
        file_path=tmp_path,
        symbols=["RELIANCE", "INFY"],
        date_range=("2022-01-01", "2022-12-31"),
        timeframe="1D",
        source_id="NSE_TEST",
        record_count=100,
    )

    fp2 = DataFingerprint.from_file(
        file_path=tmp_path,
        symbols=["INFY", "RELIANCE"],
        date_range=("2022-01-01", "2022-12-31"),
        timeframe="1D",
        source_id="NSE_TEST",
        record_count=100,
    )

    assert fp1.dataset_hash == fp2.dataset_hash
    assert fp1.symbols_hash == fp2.symbols_hash