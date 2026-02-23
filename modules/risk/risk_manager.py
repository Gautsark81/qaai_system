"""
modules/risk/risk_manager.py

Production-grade Risk Manager with
CI-enforced performance regression instrumentation.

Doctrine:
- Broker agnostic
- Deterministic
- Stability first
"""

from typing import Dict, Any

from modules.performance.timers import timed
from modules.performance.registry import PerformanceRegistry


_perf_registry = PerformanceRegistry()


class RiskDecision:
    PASSED = "PASSED"
    RISK_BLOCK = "RISK_BLOCK"
    HARD_FAIL = "HARD_FAIL"


class RiskManager:
    """
    Single source of truth for all risk decisions.
    """

    def __init__(self, rules):
        self.rules = rules

    def evaluate_risk(self, *, strategy_id: str, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate risk with strict rule dominance.
        Performance is observed but NEVER influences outcome.
        """
        with timed() as elapsed:
            decision = self._evaluate_internal(
                strategy_id=strategy_id,
                symbol=symbol,
                context=context,
            )

        _perf_registry.record("risk_eval", elapsed())

        return decision

    # --------------------------------------------------
    # INTERNAL LOGIC (UNCHANGED SEMANTICS)
    # --------------------------------------------------

    def _evaluate_internal(self, *, strategy_id: str, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        for rule in self.rules:
            result = rule.check(strategy_id, symbol, context)
            if not result["passed"]:
                return {
                    "decision": RiskDecision.RISK_BLOCK,
                    "reason": result["reason"],
                    "rule": rule.name,
                }

        return {
            "decision": RiskDecision.PASSED,
            "reason": "Risk checks passed",
            "rule": None,
        }
