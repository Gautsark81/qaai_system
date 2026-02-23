from modules.portfolio.correlation import CorrelationEngine


def test_perfect_positive_correlation():
    x = [1, 2, 3, 4]
    y = [2, 4, 6, 8]

    corr = CorrelationEngine.pearson(x, y)
    assert round(corr, 2) == 1.00


def test_uncorrelated_series():
    x = [1, 2, 3, 4]
    y = [4, 1, 3, 2]

    corr = CorrelationEngine.pearson(x, y)
    assert abs(corr) < 0.5
