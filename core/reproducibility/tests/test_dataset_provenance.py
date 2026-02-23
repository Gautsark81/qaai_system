from core.reproducibility.dataset_provenance import DatasetProvenance


def test_provenance_builds():
    p = DatasetProvenance(
        source_type="s3",
        source_identifier="bucket/data.parquet",
        snapshot_id="v1",
        symbol_list=["INFY", "TCS"],
        start_date="2023-01-01",
        end_date="2023-12-31",
        record_count=1000,
    )

    assert p.record_count == 1000
    assert sorted(p.symbol_list) == ["INFY", "TCS"]