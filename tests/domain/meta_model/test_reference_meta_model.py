from domain.meta_model.reference_meta_model import ReferenceMetaModel
from domain.meta_model.feature_contract import FeatureVector


def test_reference_model_is_deterministic():
    model = ReferenceMetaModel()
    fv = FeatureVector(values={"rsi": 55.0, "atr": 1.2}, window_id="W1")

    out1 = model.infer(fv)
    out2 = model.infer(fv)

    assert out1.p_up == out2.p_up
    assert out1.model_version == "ref-1.0"
