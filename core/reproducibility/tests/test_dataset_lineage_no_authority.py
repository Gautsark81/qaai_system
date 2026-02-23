from core.reproducibility.dataset_provenance import DatasetProvenance


def test_no_execution_surface():
    p = DatasetProvenance(
        source_type="nse_live",
        source_identifier="live_feed",
        snapshot_id="20240201",
        symbol_list=["NIFTY"],
        start_date="2024-02-01",
        end_date="2024-02-01",
        record_count=500,
    )

    assert not hasattr(p, "execute")
    assert not hasattr(p, "allocate")