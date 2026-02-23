from core.reproducibility.dataset_provenance import DatasetProvenance
from core.reproducibility.dataset_lineage_hash import DatasetLineageHasher


def test_lineage_hash_deterministic():
    p = DatasetProvenance(
        source_type="local",
        source_identifier="data.csv",
        snapshot_id="20240101",
        symbol_list=["A", "B"],
        start_date="2023-01-01",
        end_date="2023-01-31",
        record_count=100,
    )

    h1 = DatasetLineageHasher.hash(p)
    h2 = DatasetLineageHasher.hash(p)

    assert h1 == h2