from domain.meta_model.feature_contract import FeatureVector


def test_feature_vector_immutable():
    fv = FeatureVector(values={"rsi": 55.0}, window_id="W1")
    assert fv.values["rsi"] == 55.0
