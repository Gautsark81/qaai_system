# tests/test_simple_model.py
from models.simple_model import SimpleThresholdModel


def test_simple_model_fit_predict_save_load(tmp_path):
    model = SimpleThresholdModel()
    # Create tiny dataset: X rows each a list of numbers; last value used by model
    X = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    y = [0, 1, 1]
    res = model.fit(X, y)
    assert "global_mean" in res or "status" in res
    preds = model.predict([[2, 3, 4], [0, 0, 1]])
    assert isinstance(preds, list) and all(isinstance(p, int) for p in preds)
    # save and reload
    fp = tmp_path / "model.json"
    model.save(str(fp))
    # create new instance and load
    m2 = SimpleThresholdModel()
    m2.load(str(fp))
    assert isinstance(m2.params.get("global_mean"), float)


def test_predict_consistent_with_threshold(tmp_path):
    model = SimpleThresholdModel()
    X = [[1], [2], [3], [100]]
    y = [0, 0, 0, 1]
    model.fit(X, y)
    preds = model.predict([[0], [200]])
    # second should be 1 (200 > global_mean), first likely 0
    assert preds[1] == 1
