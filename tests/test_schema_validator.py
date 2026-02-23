import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data import schema_validator
import pandas as pd


def test_schema_valid():
    df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    missing, extra = schema_validator.validate_schema(
        df, ["timestamp", "open", "high", "low", "close", "volume"]
    )
    assert missing == set()
    assert extra == set()
