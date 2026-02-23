from domain.meta_model.context_adapter import MetaModelContextAdapter
from domain.meta_model.reference_meta_model import ReferenceMetaModel
from domain.meta_model.feature_contract import FeatureVector


def test_context_adapter_returns_probability():
    model = ReferenceMetaModel()
    adapter = MetaModelContextAdapter(model)

    fv = FeatureVector(values={"rsi": 60.0}, window_id="W2")
    out = adapter.get_context(fv)

    assert out.confidence >= 0.0
