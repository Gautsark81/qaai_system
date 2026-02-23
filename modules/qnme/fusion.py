# modules/qnme/fusion.py
from typing import List
from modules.strategy.base import Signal

def sequential_fusion(primary_signals: List[Signal], secondary_signals: List[Signal]) -> List[Signal]:
    """
    Simple sequential fusion: keep primary signals only if secondary confirms side for same symbol.
    """
    out = []
    sec_map = {}
    for s in secondary_signals:
        sec_map.setdefault((s.symbol, s.side), []).append(s)

    for p in primary_signals:
        if (p.symbol, p.side) in sec_map:
            # confirm; average scores if present
            sec = sec_map[(p.symbol, p.side)][0]
            new_score = ((p.score or 0.0) + (sec.score or 0.0)) / 2.0
            p.score = new_score
            out.append(p)
    return out

def weighted_union(signals_list: List[List[Signal]], weights: List[float]) -> List[Signal]:
    """
    Combine multiple signal lists with weights; deduplicate by (symbol,side) choosing weighted average score.
    """
    idx = {}
    for w, sl in zip(weights, signals_list):
        for s in sl:
            key = (s.symbol, s.side)
            if key not in idx:
                idx[key] = {"score_sum": 0.0, "weight_sum": 0.0, "example": s}
            idx[key]["score_sum"] += (s.score or 0.0) * w
            idx[key]["weight_sum"] += w
    out = []
    for k, v in idx.items():
        ex = v["example"]
        ex.score = v["score_sum"] / max(1e-6, v["weight_sum"])
        out.append(ex)
    return out
