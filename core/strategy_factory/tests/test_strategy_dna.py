from core.strategy_factory.dna import AlphaGenome


def test_alpha_genome_fingerprint_is_stable():
    g1 = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="momentum_breakout",
        filters=["liquidity", "volatility"],
        risk_model="atr_stop",
        exit_model="time_decay",
        sizing_model="confidence_weighted",
        parameters={"lookback": 20, "threshold": 1.5},
    )

    g2 = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="momentum_breakout",
        filters=["liquidity", "volatility"],
        risk_model="atr_stop",
        exit_model="time_decay",
        sizing_model="confidence_weighted",
        parameters={"lookback": 20, "threshold": 1.5},
    )

    assert g1.fingerprint() == g2.fingerprint()


def test_alpha_genome_fingerprint_changes_on_mutation():
    g1 = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="momentum_breakout",
        parameters={"lookback": 20},
    )

    g2 = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="momentum_breakout",
        parameters={"lookback": 30},
    )

    assert g1.fingerprint() != g2.fingerprint()


def test_alpha_genome_serialization_contains_fingerprint():
    g = AlphaGenome(
        allowed_regimes=["RANGE"],
        signal_type="mean_reversion",
    )

    payload = g.to_dict()

    assert "fingerprint" in payload
    assert payload["signal_type"] == "mean_reversion"
