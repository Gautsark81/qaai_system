class PromotionGate:
    """
    FINAL authority for live promotion.
    No overrides. No ML. No human shortcuts.
    """

    def eligible(self, *, stats) -> bool:
        return (
            stats.paper_days >= 30
            and stats.win_rate >= 0.80
            and stats.max_drawdown <= 0.05
            and stats.health_score >= 0.75
            and stats.no_risk_violations
        )
