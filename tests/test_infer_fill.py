# tests/test_infer_fill.py
from ml.infer_fill import FillModel


def test_infer_basic(tmp_path):
    # Use the model file saved in the repo's models/ directory
    model_path = "models/fill_model.pkl"
    fm = FillModel(model_path)
    order = {
        "symbol": "AAA",
        "side": "buy",
        "quantity": 10,
        "price": 100.0,
        "account_nav": 10000,
        "last_price": 100.0,
    }
    p = fm.predict_proba_for_order(order)
    assert 0.0 <= p <= 1.0
