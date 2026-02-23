from domain.capital.portfolio_exposure import PortfolioExposure


def test_portfolio_exposure():
    e = PortfolioExposure(
        total_deployed=500_000,
        per_symbol={"NIFTY": 200_000},
    )
    assert e.per_symbol["NIFTY"] == 200_000
