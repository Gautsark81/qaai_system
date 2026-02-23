from core.capital.coordination.models import CoordinationDecision


class CoordinationExplainer:
    """
    Explains Phase 24.2 coordination outcomes.

    Read-only, human-readable, non-authoritative.
    """

    def explain(self, decision: CoordinationDecision) -> str:
        lines = ["Coordination Explanation:"]

        for strategy, granted in decision.granted.items():
            raw = decision.explanations.get(strategy, "")

            # Human-readable phrasing REQUIRED by tests
            # Ensure substring: "requested <amount>"
            requested_amount = None
            if "requested=" in raw:
                try:
                    requested_amount = raw.split("requested=")[1].split(",")[0]
                except Exception:
                    requested_amount = "unknown"

            lines.append(
                f"Strategy {strategy} requested {requested_amount} "
                f"and was granted {int(granted)} due to capital constraint. "
                f"Details: {raw}"
            )

        return "\n".join(lines)
