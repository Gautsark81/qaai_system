from ml.meta.meta_model import MetaModel


def test_meta_model_bounds():
    m = MetaModel()
    s = m.score({"volatility": 0.9, "win_rate": 0.2})
    assert 0.0 <= s <= 1.0
