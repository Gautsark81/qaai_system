from domain.capital.capital_policy import CapitalPolicy


def test_capital_policy_fields():
    p = CapitalPolicy(
        max_total_capital=1_000_000,
        max_per_strategy_pct=0.10,
        max_per_symbol_pct=0.05,
        max_drawdown_pct=0.20,
        min_ssr=0.60,
    )
    assert p.min_ssr == 0.60
