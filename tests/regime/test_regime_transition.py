from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_transition import RegimeTransition


def _append(memory, symbol, regime, confidence=0.6):
    memory.append(
        symbol=symbol,
        regime=regime,
        confidence=confidence,
        detector_id="test",
        evidence={},
    )


def test_transition_matrix_counts():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)
    _append(memory, "NIFTY", MarketRegime.RANGING)

    rt = RegimeTransition(memory)
    matrix = rt.transition_matrix("NIFTY")

    assert matrix[(MarketRegime.RANGING, MarketRegime.TRENDING)] == 1
    assert matrix[(MarketRegime.TRENDING, MarketRegime.RANGING)] == 1


def test_last_transition():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    rt = RegimeTransition(memory)
    last = rt.last_transition("NIFTY")

    assert last["from"] == MarketRegime.RANGING
    assert last["to"] == MarketRegime.TRENDING
    assert last["at"] is not None


def test_transition_frequency():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)
    _append(memory, "NIFTY", MarketRegime.RANGING)

    rt = RegimeTransition(memory)
    freq = rt.transition_frequency("NIFTY")

    assert freq > 0.0
    assert freq <= 1.0


def test_dominant_transition():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)
    _append(memory, "NIFTY", MarketRegime.RANGING)
    _append(memory, "NIFTY", MarketRegime.TRENDING)

    rt = RegimeTransition(memory)
    dom = rt.dominant_transition("NIFTY")

    assert dom == (MarketRegime.RANGING, MarketRegime.TRENDING)


def test_no_mutation_of_memory():
    memory = RegimeMemory()

    _append(memory, "NIFTY", MarketRegime.RANGING)
    count_before = memory.count()

    rt = RegimeTransition(memory)
    _ = rt.transition_matrix("NIFTY")
    _ = rt.transition_frequency("NIFTY")

    assert memory.count() == count_before
