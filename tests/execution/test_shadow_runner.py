from data.features.store import FeatureStore
from data.features.view import FeatureView
from data.features.resolver import FeatureResolver

from data.models.artifact import ModelArtifact
from data.models.manifest import ModelManifest
from data.models.registry import ModelRegistry

from qaai_system.execution.shadow_runner import ShadowExecutionRunner
from qaai_system.execution.shadow_ledger import ShadowLedger
from data.execution.intent import ExecutionIntent


def _setup_shadow_env():
    # ---- feature setup ----
    store = FeatureStore()
    view = FeatureView(
        name="prices",
        feature_manifest_id="fm1",
        features=["open", "close"],
    )
    store.register_view(view)
    store.load(view, "NIFTY", {"open": 100, "close": 105})

    resolver = FeatureResolver(store)

    # ---- model setup ----
    artifact = ModelArtifact(
        model_id="m1",
        algo="MockModel",
        params={},
        feature_manifest_id="fm1",
        trained_on_manifest_id="d1",
    )
    manifest = ModelManifest(artifact)

    registry = ModelRegistry()
    registry.register(manifest)

    # ---- fake inference ----
    def infer_fn(features, model_manifest_id):
        assert model_manifest_id == manifest.manifest_id
        return {
            "side": "BUY",
            "quantity": 10,
        }

    return resolver, registry, infer_fn, view, manifest


def test_shadow_execution_runner():
    resolver, registry, infer_fn, view, manifest = _setup_shadow_env()

    runner = ShadowExecutionRunner(
        feature_resolver=resolver,
        model_registry=registry,
        infer_fn=infer_fn,
    )

    out = runner.run(
        strategy_id="strat1",
        symbol="NIFTY",
        feature_view=view,
        model_manifest_id=manifest.manifest_id,
    )

    intent = out["intent"]

    assert isinstance(intent, ExecutionIntent)
    assert intent.strategy_id == "strat1"
    assert intent.symbol == "NIFTY"
    assert intent.side == "BUY"
    assert intent.quantity == 10
    assert out["model_manifest_id"] == manifest.manifest_id


def test_shadow_runner_writes_to_ledger():
    ledger = ShadowLedger()

    resolver, registry, infer_fn, view, manifest = _setup_shadow_env()

    runner = ShadowExecutionRunner(
        feature_resolver=resolver,
        model_registry=registry,
        infer_fn=infer_fn,
        ledger=ledger,
    )

    runner.run(
        strategy_id="strat1",
        symbol="NIFTY",
        feature_view=view,
        model_manifest_id=manifest.manifest_id,
    )

    records = ledger.all()
    assert len(records) == 1

    rec = records[0]

    # --- top-level shadow metadata ---
    assert rec["strategy_id"] == "strat1"
    assert rec["symbol"] == "NIFTY"
    assert rec["model_manifest_id"] == manifest.manifest_id

    # --- execution intent snapshot ---
    intent = rec["intent"]
    assert isinstance(intent, ExecutionIntent)
    assert intent.side == "BUY"
    assert intent.quantity == 10
