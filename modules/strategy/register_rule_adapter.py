# modules/strategy/register_rule_adapter.py
from modules.strategy.factory import register_strategy
from modules.strategy.rule_adapter import RuleEngineAdapter

register_strategy("RuleEngineAdapter")(RuleEngineAdapter)
