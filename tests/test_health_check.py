import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.ingestion import fetch_data


def run_health_check():
    try:
        df = fetch_data("TCS", "2023-01-01", "2023-01-05")
        assert df is not None and not df.empty
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
