class GovernanceExplainer:
    """
    Explains governance allow/deny decisions.
    """

    def explain(self, allowed: bool, rule: str, phase: str) -> str:
        if allowed:
            return (
                f"Action permitted under rule {rule} "
                f"as validated in {phase}."
            )
        return (
            f"Action denied due to rule {rule} "
            f"as enforced in {phase}."
        )
