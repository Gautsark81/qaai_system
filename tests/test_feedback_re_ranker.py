# File: watchlist/feedback_re_ranker.py

import os
import pandas as pd
import logging
from river import linear_model, naive_bayes, tree
from watchlist.base_re_ranker import BaseReRanker


logger = logging.getLogger(__name__)


class FeedbackReRanker(BaseReRanker):
    def __init__(self, confidence_threshold=0.7):
        super().__init__()
        self.confidence_threshold = confidence_threshold
        self.model = self._load_model()

    def _load_model(self):
        model_type = os.getenv("FEEDBACK_MODEL_TYPE", "").lower()
        (
            logger.info(f"🧠 Overriding model via env: {model_type}")
            if model_type
            else None
        )

        if model_type == "naive_bayes":
            model = naive_bayes.GaussianNB()
        elif model_type == "hoeffding_tree":
            model = tree.HoeffdingTreeClassifier()
        else:
            model = linear_model.LogisticRegression()

        logger.info(f"🔎 Selected model: {model.__class__.__name__}")
        return [model]

    def run(self):
        logger.info("🔁 Running feedback-based re-ranking...")

        watchlist = self.db.fetch_watchlist_with_feedback()
        if watchlist is None or isinstance(watchlist, list):
            watchlist = pd.DataFrame(
                watchlist, columns=["symbol", "features", "label", "feedback_time"]
            )
        if watchlist.empty:
            logger.warning("⚠️ No watchlist data found for re-ranking.")
            return []

        logger.info(f"📊 Retrieved {len(watchlist)} symbols from watchlist.")

        for row in watchlist.itertuples(index=False):
            symbol = row.symbol
            features = row.features
            label = row.label
            feedback_time = row.feedback_time
            decay = self._compute_time_decay(feedback_time)
            self.model[-1].learn_one(features, int(label) * decay)

        scored = []
        for row in watchlist.itertuples(index=False):
            symbol = row.symbol
            features = row.features
            proba = self.model[-1].predict_proba_one(features)
            score = proba.get(1, 0)
            logger.debug(f"📈 {symbol} score: {score:.4f}")
            if score >= self.confidence_threshold:
                scored.append((symbol, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        re_ranked = [s[0] for s in scored]
        logger.info(f"✅ Final re-ranked symbols: {re_ranked}")
        return re_ranked
