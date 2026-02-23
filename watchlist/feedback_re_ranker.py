# File: watchlist/feedback_re_ranker.py

import os
import pickle
import math
from datetime import datetime

from river import linear_model, naive_bayes, tree, preprocessing
from infra.db_client import DBClient
from infra.logging_utils import get_logger

logger = get_logger("feedback_re_ranker")


class FeedbackReRanker:
    def __init__(
        self,
        top_n=50,
        confidence_threshold=0.6,
        model_path="models/feedback_model.pkl",
        model_type="logistic",
    ):
        self.top_n = top_n
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.model_type = self.get_model_type(default=model_type)
        self.db = DBClient()
        self.model = self._load_model()

    def get_model_type(self, default=None):
        """Check env override; fallback to default/model_type."""
        env_model = os.getenv("FEEDBACK_MODEL_TYPE")
        if env_model:
            model_type = env_model.lower()
            logger.info(f"🧠 Overriding model via env: {model_type}")
            return model_type
        return default.lower() if default else "logistic"

    def _select_model(self):
        """Choose River model based on type."""
        if self.model_type == "logistic":
            logger.info("🔎 Selected model: Logistic Regression")
            return preprocessing.StandardScaler() | linear_model.LogisticRegression()
        elif self.model_type == "naive_bayes":
            logger.info("🔎 Selected model: Naive Bayes")
            return preprocessing.StandardScaler() | naive_bayes.GaussianNB()
        elif self.model_type == "hoeffding_tree":
            logger.info("🔎 Selected model: Hoeffding Tree")
            return preprocessing.StandardScaler() | tree.HoeffdingTreeClassifier()
        else:
            logger.warning(
                f"⚠️ Unknown model type '{self.model_type}', defaulting to Logistic Regression."
            )
            return preprocessing.StandardScaler() | linear_model.LogisticRegression()

    def _load_model(self):
        """Load model from disk or initialize new."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    model = pickle.load(f)
                    logger.info(f"📦 Loaded model from {self.model_path}")
                    return model
            except Exception as e:
                logger.warning(f"⚠️ Failed to load model, using new one. Reason: {e}")
        return self._select_model()

    def _save_model(self):
        """Persist the model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        logger.info("💾 Model saved successfully.")

    def _time_decay_weight(self, feedback_time):
        """Apply time decay to feedback weight."""
        now = datetime.utcnow()
        delta = (now - feedback_time).total_seconds() / 3600  # hours
        decay = math.exp(-0.05 * delta)
        return decay

    def run(self):
        logger.info("🔁 Running feedback-based re-ranking...")

        watchlist = self.db.fetch_watchlist_with_feedback()
        if watchlist is None or watchlist.empty:
            logger.warning("⚠️ No watchlist data found for re-ranking.")
            return []

        logger.info(f"📊 Retrieved {len(watchlist)} symbols from watchlist.")

        # Train model using decayed feedback
        for symbol, features, label, feedback_time in watchlist:
            weight = self._time_decay_weight(feedback_time)
            self.model.learn_one(features, label, weight=weight)

        # Score and apply confidence threshold
        scored = []
        for symbol, features, _, _ in watchlist:
            score = self.model.predict_proba_one(features).get(True, 0.0)
            if score >= self.confidence_threshold:
                scored.append((symbol, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_symbols = [s for s, _ in scored[: self.top_n]]

        logger.info(f"🏆 Top {len(top_symbols)} symbols after filtering: {top_symbols}")

        # Update DB
        self.db.clear_watchlist()
        self.db.insert_watchlist(top_symbols)
        logger.info("✅ Watchlist updated after re-ranking.")

        # Save model
        self._save_model()

        return top_symbols
