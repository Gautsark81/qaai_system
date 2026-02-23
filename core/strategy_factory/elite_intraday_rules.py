# core/strategy_factory/elite_intraday_rules.py

class EliteIntradayRules:
    """
    Intraday rule checks.

    HARD RULE:
    - Rules must NEVER raise KeyError
    - Missing context ⇒ condition evaluates to False
    """

    @staticmethod
    def is_buy_zone(ctx: dict) -> bool:
        return (
            ctx.get("trade_direction") == "BUY"
            and ctx.get("price_above_vwap", False)
            and ctx.get("supertrend_direction") == "BUY"
        )

    @staticmethod
    def is_sell_zone(ctx: dict) -> bool:
        return (
            ctx.get("trade_direction") == "SELL"
            and ctx.get("price_below_vwap", False)
            and ctx.get("supertrend_direction") == "SELL"
        )
