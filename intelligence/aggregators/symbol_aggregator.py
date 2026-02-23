from collections import defaultdict


class SymbolAggregator:
    def aggregate(self, trades):
        by_symbol = defaultdict(list)
        for t in trades:
            by_symbol[t.symbol].append(t)

        metrics = {}
        for sym, ts in by_symbol.items():
            total = len(ts)
            success = sum(t.net_r > 0 for t in ts)
            metrics[sym] = {
                "total_trades": total,
                "successful_trades": success,
                "ssr": success / total if total else 0.0,
            }
        return metrics
