from core.alpha.screening.liquidity.engine import run_liquidity_survivability
from core.alpha.screening.liquidity.artifacts import emit_distributions


def run_liquidity_batch(symbol_rows):
    """
    Run liquidity survivability across many symbols.
    """
    rows = []

    for row in symbol_rows:
        verdict = run_liquidity_survivability(**row)

        evidence_map = {e.metric: e.value for e in verdict.evidence}
        rows.append({
            "symbol": verdict.symbol,
            "order_pct_adv": evidence_map["order_pct_adv"],
            "exit_days": evidence_map["exit_days"],
        })

    emit_distributions(rows)
