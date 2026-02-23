# modules/qnme/gates.py
from typing import Callable, Dict, Any, Tuple, List
import math
import statistics
import logging

logger = logging.getLogger(__name__)

GateResult = Tuple[bool, str, float]
Gate = Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]], GateResult]
# signature: gate(signal_struct, tick, genome, regime) -> (ok, reason, score_delta)

def hidden_liquidity_gate(signal_struct, tick, genome, regime) -> GateResult:
    """
    If the signal appears near an inferred large order block, reject.
    Simple heuristic: if liquidity_p_large > 0.6 and signal side conflicts with imbalance -> reject.
    """
    g = genome.get("genome", {})
    if g.get("liquidity_p_large", 0.0) > 0.6:
        imbalance = g.get("imbalance", 0.0)
        side = signal_struct["signal"].side
        if (imbalance > 0 and side == "SELL") or (imbalance < 0 and side == "BUY"):
            return False, "hidden_liquidity_conflict", -1.0
    return True, "ok", 0.0

def spread_widening_gate(signal_struct, tick, genome, regime) -> GateResult:
    """
    Reject if spread is unusually wide in the last window.
    Expects tick to have 'spread' and genome to have 'avg_dt' as proxy.
    """
    spread = tick.get("spread")
    avg_dt = genome.get("genome", {}).get("avg_dt", 0.0)
    if spread is not None and avg_dt > 0:
        # simple threshold: if spread > k * median-spread proxy -> reject
        if spread > max(1.0, 0.02 * tick.get("price", 1.0)):
            return False, "spread_widening", -0.5
    return True, "ok", 0.0

def ma_alignment_gate(signal_struct, tick, genome, regime) -> GateResult:
    """
    Example: require that microstructure trend aligns with signal side.
    This is a placeholder that always passes.
    """
    return True, "ok", 0.0

class GatePipeline:
    def __init__(self, gates: List[Gate] = None):
        self.gates = gates or [hidden_liquidity_gate, spread_widening_gate, ma_alignment_gate]

    def validate(self, candidate: Dict[str, Any], tick: Dict[str, Any], genome: Dict[str, Any], regime: Dict[str, Any]) -> Tuple[bool, List[Tuple[str, str, float]]]:
        results = []
        for g in self.gates:
            try:
                ok, reason, delta = g(candidate, tick, genome, regime)
            except Exception:
                logger.exception("Gate raised")
                return False, [("gate_error", "exception", -10.0)]
            results.append((g.__name__, reason, delta))
            if not ok:
                return False, results
        return True, results
