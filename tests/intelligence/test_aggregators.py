from intelligence.aggregators.symbol_aggregator import SymbolAggregator

class DummyTrade:
    def __init__(self, symbol, net_r):
        self.symbol = symbol
        self.net_r = net_r


def test_symbol_aggregation():
    trades = [
        DummyTrade("NIFTY", 1),
        DummyTrade("NIFTY", -1),
        DummyTrade("BANKNIFTY", 2),
    ]

    agg = SymbolAggregator().aggregate(trades)
    assert agg["NIFTY"]["total_trades"] == 2
    assert agg["BANKNIFTY"]["ssr"] == 1.0
