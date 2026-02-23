# tests/universe/test_universe_service.py
from universe.service import UniverseService, SymbolMetadata


def test_universe_upsert_and_persistence(tmp_path):
    base_dir = tmp_path / "universe"
    us = UniverseService(base_dir=str(base_dir))

    us.upsert_symbol("NIFTY", sector="INDEX", segment="FNO")
    us.upsert_symbol("RELIANCE", sector="ENERGY", segment="EQ")
    us.upsert_symbol("HDFCBANK", sector="FINANCIALS", segment="EQ")

    # basic queries
    assert us.sector("RELIANCE") == "ENERGY"
    assert set(us.all_symbols()) == {"NIFTY", "RELIANCE", "HDFCBANK"}

    # persistence
    us2 = UniverseService(base_dir=str(base_dir))
    assert set(us2.all_symbols()) == {"NIFTY", "RELIANCE", "HDFCBANK"}
    assert us2.sector("NIFTY") == "INDEX"


def test_universe_sector_filters(tmp_path):
    base_dir = tmp_path / "universe"
    us = UniverseService(base_dir=str(base_dir))

    us.upsert_symbol("RELIANCE", sector="ENERGY")
    us.upsert_symbol("ONGC", sector="ENERGY")
    us.upsert_symbol("HDFCBANK", sector="FINANCIALS")
    us.upsert_symbol("ICICIBANK", sector="FINANCIALS")
    us.upsert_symbol("INFY", sector="IT")

    energy = us.universe_by_sector(["ENERGY"])
    assert set(energy) == {"RELIANCE", "ONGC"}

    fin_only = us.universe_by_sector(["FINANCIALS"])
    assert set(fin_only) == {"HDFCBANK", "ICICIBANK"}

    # filter_symbols on a mixed list
    mixed = ["RELIANCE", "HDFCBANK", "INFY"]
    only_energy = us.filter_symbols(mixed, include_sectors=["ENERGY"])
    assert only_energy == ["RELIANCE"]

    exclude_fin = us.filter_symbols(mixed, exclude_sectors=["FINANCIALS"])
    # INFY may be omitted because its sector is IT (not excluded)
    assert set(exclude_fin) == {"RELIANCE", "INFY"}
