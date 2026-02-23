from collections import defaultdict


class RegimeAggregator:
    def aggregate(self, trades):
        by_regime = defaultdict(list)
        for t in trades:
            by_regime[getattr(t, "regime", "UNKNOWN")].append(t)

        out = {}
        for regime, ts in by_regime.items():
            total = len(ts)
            success = sum(t.net_r > 0 for t in ts)
            out[regime] = {
                "total_trades": total,
                "successful_trades": success,
                "ssr": success / total if total else 0.0,
            }
        return out
