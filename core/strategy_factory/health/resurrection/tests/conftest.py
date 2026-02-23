import pytest
from datetime import datetime

from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.compiler.compiler import StrategyCompiler
from core.strategy_factory.grammar.ast import ASTNode
from core.strategy_factory.grammar.primitives import Primitive

from core.strategy_factory.health.decay.model import DecaySnapshot


# ============================================================
# Core Fixtures
# ============================================================

@pytest.fixture
def registry():
    return StrategyRegistry()


@pytest.fixture
def compiler():
    return StrategyCompiler()


@pytest.fixture
def strategy_spec(compiler):
    """
    Create a REAL StrategySpec via compiler to ensure
    DNA computation works correctly.
    """
    ast = ASTNode(Primitive("Momentum", 20))
    return compiler.compile(ast)


@pytest.fixture
def record(registry, strategy_spec):
    """
    Register a valid strategy and return StrategyRecord.
    """
    return registry.register(strategy_spec)


# ============================================================
# Mutated / Scenario Fixtures
# ============================================================

@pytest.fixture
def mock_record(record):
    """
    Retired strategy eligible for resurrection.
    """
    record.state = "RETIRED"
    record.flags = {}
    record.metadata = {}
    return record


@pytest.fixture
def decay():
    """
    Decay snapshot indicating possible regime revival.
    """
    return DecaySnapshot(
        dna="dummy_dna",
        decay_score=0.6,
        historical_edge=1.2,
        regime="TREND",
        regime_shift_detected=True,
        data_expansion=False,
        timestamp=datetime.utcnow(),
        notes=None,
    )


@pytest.fixture
def mock_decay(decay):
    return decay
