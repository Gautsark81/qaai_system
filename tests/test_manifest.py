# tests/test_manifest.py
from modules.data_pipeline.manifest import make_manifest, validate_manifest, checksum_of_rows_for_manifest_symbol

def test_manifest_and_validate():
    m = make_manifest("FOO", 10, "2025-01-05")
    assert m["symbol"] == "FOO"
    assert m["rows"] == 10
    assert validate_manifest(m)
    # checksum deterministic
    expected = checksum_of_rows_for_manifest_symbol(10, "FOO", "2025-01-05")
    assert m["checksum"] == expected
