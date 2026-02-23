# tests/test_meta_model.py
import numpy as np
import pytest

sklearn = pytest.importorskip("sklearn")
joblib = pytest.importorskip("joblib")

from modules.meta.model import MetaModel

def test_meta_model_train_and_predict(tmp_path):
    # Synthetic dataset: 100 samples, 5 features, labels in {1,-1,0}
    rng = np.random.RandomState(0)
    X = rng.randn(100, 5)
    # create labels by simple rule on first feature
    y = np.where(X[:, 0] > 0.8, 1, np.where(X[:, 0] < -0.8, -1, 0))

    mm = MetaModel(n_estimators=10, random_state=0)
    stats = mm.fit(X, y)
    assert "accuracy" in stats

    # predict a single vector
    v = X[0]
    probs = mm.predict_proba(v)
    assert set(probs.keys()) == {"p_buy", "p_sell", "p_hold"}

    fn = str(tmp_path / "mm.joblib")
    mm.save(fn)

    mm2 = MetaModel(n_estimators=1)
    mm2.load(fn)
    out = mm2.predict_proba(v)
    assert set(out.keys()) == {"p_buy", "p_sell", "p_hold"}
