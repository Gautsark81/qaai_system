from domain.model_ops.model_id import ModelID


def test_model_id_immutable():
    m = ModelID("meta_model", "1.0.0", "abc")
    assert m.version == "1.0.0"
