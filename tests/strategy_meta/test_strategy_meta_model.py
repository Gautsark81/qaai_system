from modules.strategy_meta.meta_model import MetaModel
from modules.strategy_meta.training_sample import MetaTrainingSample
from modules.strategy_meta.advisory_selector import AdvisorySelector


def test_meta_model_training_and_scoring():
    samples = [
        MetaTrainingSample(
            strategy_id="s1",
            symbol="NIFTY",
            regime="LOW_VOL",
            features={"vol": 0.2, "trend": 0.7},
            label=1.0,
        ),
        MetaTrainingSample(
            strategy_id="s1",
            symbol="NIFTY",
            regime="LOW_VOL",
            features={"vol": 0.25, "trend": 0.75},
            label=1.0,
        ),
    ]

    model = MetaModel(feature_weights={"vol": 1.0, "trend": 1.0})
    model.train(samples)

    score = model.score(
        strategy_id="s1",
        regime="LOW_VOL",
        context_features={"vol": 0.22, "trend": 0.72},
    )

    assert score > 0.5


def test_meta_model_explain():
    samples = [
        MetaTrainingSample(
            strategy_id="s2",
            symbol="BANKNIFTY",
            regime="HIGH_VOL",
            features={"vol": 0.8, "trend": 0.3},
            label=0.8,
        ),
    ]

    model = MetaModel(feature_weights={"vol": 2.0, "trend": 1.0})
    model.train(samples)

    explanation = model.explain(
        strategy_id="s2",
        regime="HIGH_VOL",
        context_features={"vol": 0.7, "trend": 0.4},
    )

    assert "vol" in explanation
    assert explanation["vol"] > 0.0


def test_advisory_selector_ranks():
    samples = [
        MetaTrainingSample(
            strategy_id="a",
            symbol="NIFTY",
            regime="LOW_VOL",
            features={"vol": 0.2},
            label=1.0,
        ),
        MetaTrainingSample(
            strategy_id="b",
            symbol="NIFTY",
            regime="LOW_VOL",
            features={"vol": 0.6},
            label=0.5,
        ),
    ]

    model = MetaModel(feature_weights={"vol": 1.0})
    model.train(samples)

    selector = AdvisorySelector(model)

    ranked = selector.rank(
        strategies=["a", "b"],
        regime="LOW_VOL",
        context_features={"vol": 0.25},
    )

    assert list(ranked.keys())[0] == "a"
