from core.alpha.screening.regime.engine import run_regime_admissibility
from core.alpha.screening.regime.artifacts import emit_regime_distributions


def run_regime_batch(symbol_rows):
    """
    Run regime admissibility across multiple symbols.
    """

    rows = []

    for row in symbol_rows:
        verdict = run_regime_admissibility(**row)

        evidence_map = {e.metric: e.value for e in verdict.evidence}

        rows.append({
            "volatility_ratio": evidence_map["volatility_ratio"],
            "trend_strength": evidence_map["trend_strength"],
        })

    emit_regime_distributions(rows)
