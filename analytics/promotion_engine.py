# qaai_system/analytics/promotion_engine.py
from __future__ import annotations
import json, logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

from strategies.registry import load_registry
from analytics.strategy_metrics import METRICS_PATH
from analytics.meta_model import StrategyMetaModel, MetaModelFeatures
from data.universe_loader import load_universe_for_date

logger = logging.getLogger(__name__)
DAILY_PLAN_DIR = Path("configs/daily_run_plan")
DAILY_PLAN_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class DailyAssignment:
    symbol: str
    strategy_id: str
    version: str
    capital_fraction: float
    score: float

def _load_metrics():
    if not METRICS_PATH.exists(): return {}
    with METRICS_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    by_key={}
    for row in raw:
        by_key[(row["strategy_id"], str(row["version"]), row["run_mode"])] = row
    return by_key

def build_daily_run_plan(for_date: date, mode: str="paper") -> Path:
    plan_path = DAILY_PLAN_DIR / f"{for_date.isoformat()}.json"
    universe = load_universe_for_date(for_date)
    registry = load_registry()
    metrics_by_key = _load_metrics()
    meta_model = StrategyMetaModel()
    assignments=[]
    for member in universe.members:
        symbol=member["symbol"]
        best=None
        for sid,s_cfg in registry.get("strategies",{}).items():
            for ver,vcfg in s_cfg.get("versions",{}).items():
                status = vcfg.get("status")
                if status not in {"Paper-Approved","Live-Approved"}: continue
                perf = metrics_by_key.get((sid,str(ver),"paper")) or metrics_by_key.get((sid,str(ver),"backtest"))
                if not perf: continue
                if perf.get("trades",0) < 50: continue
                if perf.get("win_rate",0.0) < 0.8: continue
                if perf.get("profit_factor",0.0) < 1.4: continue
                feat = MetaModelFeatures(strategy_id=sid, version=str(ver), symbol=symbol,
                                         win_rate=float(perf.get("win_rate",0.0)),
                                         profit_factor=float(perf.get("profit_factor",0.0)),
                                         net_pnl=float(perf.get("net_pnl",0.0)))
                score = meta_model.score(feat)
                candidate = DailyAssignment(symbol=symbol, strategy_id=sid, version=str(ver), capital_fraction=float(vcfg.get("capital_allocation",0.0)), score=score)
                if best is None or candidate.score>best.score: best=candidate
        if best: assignments.append(best)
    payload={"as_of":for_date.isoformat(),"mode":mode,"assignments":[a.__dict__ for a in assignments]}
    with plan_path.open("w", encoding="utf-8") as f: json.dump(payload,f,indent=2)
    logger.info("Built daily run plan", extra={"path":str(plan_path),"num_assignments":len(assignments)})
    return plan_path
