import hashlib
from datetime import time

from .job import ShadowTrainingJob
from .errors import RetrainingError


class ShadowRetrainingOrchestrator:
    """
    Bridges Phase F retraining decisions to shadow training jobs.
    """

    def __init__(
        self,
        *,
        training_queue,
        audit_sink,
        clock,
        market_open: time = time(9, 15),
        market_close: time = time(15, 30),
    ):
        self.training_queue = training_queue
        self.audit_sink = audit_sink
        self.clock = clock
        self.market_open = market_open
        self.market_close = market_close
        self._seen_jobs = set()

    def _in_market_hours(self) -> bool:
        now = self.clock.utcnow().time()
        return self.market_open <= now <= self.market_close

    def _job_id(self, model_id, plan) -> str:
        raw = (
            f"{model_id}:"
            f"{plan.regime}:"
            f"{plan.lookback_days}:"
            f"{plan.model_family}:"
            f"{plan.featureset}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def schedule(
        self,
        model_id: str,
        decision,
        plan,
    ) -> ShadowTrainingJob | None:
        """
        Schedule a shadow retraining job if allowed.
        """

        if not decision.should_retrain:
            return None

        if self._in_market_hours():
            raise RetrainingError("Retraining blocked during market hours")

        job_id = self._job_id(model_id, plan)

        if job_id in self._seen_jobs:
            return None  # idempotent

        job = ShadowTrainingJob(
            job_id=job_id,
            model_id=model_id,
            regime=plan.regime,
            lookback_days=plan.lookback_days,
            model_family=plan.model_family,
            featureset=plan.featureset,
            reasons=plan.reasons,
        )

        self.training_queue.enqueue(job)
        self._seen_jobs.add(job_id)

        self.audit_sink.emit(
            {
                "event": "shadow_retraining_scheduled",
                "model_id": model_id,
                "job_id": job_id,
                "reasons": plan.reasons,
                "timestamp": self.clock.utcnow(),
            }
        )

        return job
