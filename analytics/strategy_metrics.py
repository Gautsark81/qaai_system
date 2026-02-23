# qaai_system/analytics/strategy_metrics.py
from __future__ import annotations
import dataclasses, json, logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
TRADES_DIR = Path("data/trades")   # backtests/paper/live trade logs should be placed here
METRICS_PATH = Path("data/metrics/strategy_performance.json")

@dataclass
class StrategyPerformance:
    strategy_id: str
    version: str
    run_mode: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    net_pnl: float

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

def _iter_trade_files() -> List[Path]:
    if not TRADES_DIR.exists():
        return []
    return [p for p in TRADES_DIR.rglob("*.jsonl")]

def _agg_metrics_for_group(trades: List[Dict[str, Any]]) -> StrategyPerformance:
    sample = trades[0]
    sid = sample["strategy_id"]
    ver = str(sample.get("version", "1"))
    mode = sample.get("run_mode", "paper")
    wins=losses=0
    gross_profit=gross_loss=0.0
    for t in trades:
        pnl = float(t.get("pnl",0.0))
        if pnl>0:
            wins+=1; gross_profit+=pnl
        elif pnl<0:
            losses+=1; gross_loss+=abs(pnl)
    total_trades=len(trades)
    win_rate = wins/total_trades if total_trades>0 else 0.0
    profit_factor = (gross_profit/gross_loss) if gross_loss>0 else (float("inf") if gross_profit>0 else 0.0)
    return StrategyPerformance(
        strategy_id=sid, version=ver, run_mode=mode, trades=total_trades,
        wins=wins, losses=losses, win_rate=win_rate, gross_profit=gross_profit,
        gross_loss=gross_loss, profit_factor=profit_factor, net_pnl=gross_profit - gross_loss
    )

def recompute_strategy_metrics() -> Path:
    TRADES_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    for path in _iter_trade_files():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                t = json.loads(line)
                key = (t["strategy_id"], str(t.get("version","1")), t.get("run_mode","paper"))
                groups[key].append(t)
    metrics=[]
    for (sid, ver, mode), trades in groups.items():
        perf = _agg_metrics_for_group(trades)
        metrics.append(perf.to_dict())
    with METRICS_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Recomputed strategy metrics", extra={"metrics_path": str(METRICS_PATH), "num_groups": len(metrics)})
    return METRICS_PATH
