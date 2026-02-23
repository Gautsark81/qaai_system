# File: tests/test_watchlist.py

import pytest
from infra.db_client import DBClient


@pytest.fixture(scope="module")
def db():
    client = DBClient()
    yield client
    client.close()


def test_fetch_watchlist_not_empty(db):
    symbols = db.fetch_watchlist()
    assert isinstance(symbols, list), "Watchlist should be a list"
    assert all(isinstance(s, str) for s in symbols), "Each symbol should be a string"
    assert len(symbols) > 0, "Watchlist should not be empty"
