import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data import cleaner
import pandas as pd


def test_cleaner_filters_volume():
    df = pd.DataFrame({"close": [100, 102], "volume": [1000, 0]})
    clean_df = cleaner.clean_data(df)
    assert all(clean_df["volume"] > 0)
