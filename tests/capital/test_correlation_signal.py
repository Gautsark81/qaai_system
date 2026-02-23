from modules.capital.correlation_signal import CorrelationSignal


def test_no_correlation_no_penalty():
    signal = CorrelationSignal()

    series = {
        "A": [1, 2, 3],
        "B": [3, 1, 2],
    }
    weights = {"A": 0.5, "B": 0.5}

    scale, _ = signal.scale_from_series(series=series, weights=weights)
    assert scale == 1.0


def test_high_correlation_penalty():
    signal = CorrelationSignal()

    series = {
        "A": [1, 2, 3],
        "B": [2, 4, 6],
    }
    weights = {"A": 0.8, "B": 0.2}

    scale, reason = signal.scale_from_series(series=series, weights=weights)

    assert scale < 1.0
    assert "HighCorrPairs" in reason
