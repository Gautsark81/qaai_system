# modules/qnme/anomaly.py
from typing import Dict, Tuple, Any

def detect_anomaly(genome: Dict[str, Any], tick: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Simple anomaly detection heuristics:
    - very short avg_dt + huge spread => microburst
    - imbalance > threshold => possible spoofing/large footprint
    Returns: (is_anomaly: bool, reason: str)
    """
    g = genome.get("genome", {})
    avg_dt = g.get("avg_dt", 999999)
    imbalance = abs(g.get("imbalance", 0.0))
    spread = tick.get("spread", 0.0)
    price = tick.get("price", 1.0)

    # microburst: many trades in tiny time + large spread relative to price
    if avg_dt is not None and avg_dt < 5 and spread > 0.05 * price:
        return True, "microburst_spread"

    # reduce threshold so moderate but large imbalance is flagged in tests / practice
    # (original threshold was 1000; 100 is more sensitive and matches test expectation)
    if imbalance > 100:
        return True, "large_imbalance"

    # unusually large spread relative to price (fallback)
    if spread > 0.5 * price:
        return True, "extreme_spread"

    return False, ""
