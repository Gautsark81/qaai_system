# File: tests/test_auto_updater.py

import sys
import os
import unittest
from unittest.mock import patch
from watchlist.auto_watchlist_builder import AutoWatchlistBuilder

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestAutoWatchlistBuilder(unittest.TestCase):

    @patch("watchlist.auto_watchlist_builder.DhanClient")
    @patch("watchlist.auto_watchlist_builder.DBClient")
    def test_update_watchlist_success(self, mock_db, mock_dhan):
        mock_dhan.return_value.get_top_nse_stocks_by_volume.return_value = [
            "RELIANCE",
            "TCS",
            "INFY",
        ]
        builder = AutoWatchlistBuilder(top_n=3)
        builder.update_watchlist()

        mock_db.return_value.clear_watchlist.assert_called_once()
        mock_db.return_value.insert_watchlist.assert_called_once_with(
            ["RELIANCE", "TCS", "INFY"]
        )

    @patch("watchlist.auto_watchlist_builder.DhanClient")
    def test_update_watchlist_failure(self, mock_dhan):
        mock_dhan.return_value.get_top_nse_stocks_by_volume.side_effect = Exception(
            "API Error"
        )
        builder = AutoWatchlistBuilder()
        builder.update_watchlist()  # Should not raise error, just log


if __name__ == "__main__":
    unittest.main()
