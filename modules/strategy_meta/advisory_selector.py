from typing import Dict, List

from modules.strategy_meta.meta_model import MetaModel


class AdvisorySelector:
    """
    Ranks strategies for a symbol using meta-model scores.
    Advisory only.
    """

    def __init__(self, meta_model: MetaModel):
        self.meta_model = meta_model

    def rank(
        self,
        *,
        strategies: List[str],
        regime: str,
        context_features: Dict[str, float],
    ) -> Dict[str, float]:
        scores = {
            sid: self.meta_model.score(
                strategy_id=sid,
                regime=regime,
                context_features=context_features,
            )
            for sid in strategies
        }
        return dict(sorted(scores.items(), key=lambda x: -x[1]))
