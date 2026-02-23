class EvidenceAlphaAdapter:
    """
    Evidence adapter for v2 intelligence.

    🚨 v2 NEVER writes evidence.
    It can only emit alpha annotations for downstream systems.
    """

    def emit_alpha_evidence(
        self,
        *,
        strategy_id: str,
        alpha_score: float,
        verdict: str,
    ) -> dict:
        return {
            "strategy_id": strategy_id,
            "alpha_score": alpha_score,
            "verdict": verdict,
            "source": "v2_intelligence",
        }
