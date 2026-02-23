# modules/qnme/tests/test_strategy_pool_expanded.py
from modules.qnme.strategy_pool_expanded import register_all, STRATEGY_TEMPLATES
from modules.qnme.strategy_pool import StrategyPool

def test_register_30():
    pool = StrategyPool()
    register_all(pool)
    names = pool.list_strategies()
    assert len(names) == len(STRATEGY_TEMPLATES)
