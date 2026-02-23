from datetime import datetime
from typing import Dict, Any

from data.features.resolver import FeatureResolver
from data.features.view import FeatureView
from data.models.registry import ModelRegistry
from data.execution.intent import ExecutionIntent
from execution.shadow_ledger import ShadowLedger


class ShadowExecutionRunner:
    """
    Executes the full inference + intent pipeline in shadow mode.
    """

    def __init__(
        self,
        *,
        feature_resolver: FeatureResolver,
        model_registry: ModelRegistry,
        infer_fn,
        ledger: ShadowLedger | None = None,
    ):
        self._resolver = feature_resolver
        self._registry = model_registry
        self._infer_fn = infer_fn
        self._ledger = ledger

    def run(
        self,
        *,
        strategy_id: str,
        symbol: str,
        feature_view: FeatureView,
        model_manifest_id: str,
    ) -> Dict[str, Any]:
        features = self._resolver.resolve(
            view=feature_view,
            entity_key=symbol,
            expected_feature_manifest_id=feature_view.feature_manifest_id,
        )

        prediction = self._infer_fn(features, model_manifest_id)

        intent = ExecutionIntent(
            strategy_id=strategy_id,
            symbol=symbol,
            side=prediction["side"],
            quantity=prediction["quantity"],
            order_type="MARKET",
            price=None,
            signal_time=datetime.utcnow().isoformat(),
            feature_manifest_id=feature_view.feature_manifest_id,
            model_id=model_manifest_id,
        )

        record = {
            "ts": datetime.utcnow().isoformat(),
            "strategy_id": strategy_id,
            "symbol": symbol,
            "model_manifest_id": model_manifest_id,
            "feature_view_id": feature_view.view_id,
            "features": features,
            "prediction": prediction,
            "intent": intent,
        }

        if self._ledger is not None:
            self._ledger.append(record)

        return record
