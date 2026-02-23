from unittest.mock import patch
from infra.dhan_client import DhanClient


@patch("infra.dhan_client.requests.get")
def test_fetch_ohlcv_success(mock_get):
    mock_response = {
        "data": [
            {"o": 100, "h": 105, "l": 95, "c": 102, "v": 100000, "t": "2025-07-01"},
            {"o": 102, "h": 106, "l": 98, "c": 104, "v": 110000, "t": "2025-07-02"},
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    client = DhanClient()
    result = client.fetch_ohlcv("RELIANCE", "2025-07-01", "2025-07-31")

    assert isinstance(result, list)
    assert result[0]["o"] == 100
