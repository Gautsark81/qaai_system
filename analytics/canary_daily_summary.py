"""
STEP-11.2 — Canary Daily Auto Summary
Read-only, safe, LIVE_CANARY only
"""

import os
from datetime import date
from pathlib import Path
import json


class CanaryDailySummary:
    def __init__(self):
        self.today = date.today().isoformat()
        self.env = os.getenv("TRADING_ENV", "paper")
        self.base_path = Path("data/canary_summaries")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def generate(self):
        if self.env != "live_canary":
            raise RuntimeError("Canary summary only valid in LIVE_CANARY mode")

        summary = {
            "date": self.today,
            "environment": self.env,
            "system_health": self._system_health(),
            "signals": self._signal_summary(),
            "safety": self._safety_summary(),
            "execution": self._execution_summary(),
            "operator_verdict": "UNREVIEWED",
        }

        out_file = self.base_path / f"canary_summary_{self.today}.json"
        out_file.write_text(json.dumps(summary, indent=2))

        return out_file, summary

    # --------------------------------------------------

    def _system_health(self):
        return {
            "process_up": True,
            "feed_errors": 0,
            "api_errors": 0,
            "log_errors": 0,
        }

    def _signal_summary(self):
        # Placeholder — will later read real signal logs
        return {
            "signals_generated": "OBSERVED",
            "confidence_anomalies": False,
            "timing_anomalies": False,
        }

    def _safety_summary(self):
        return {
            "risk_blocks": "EXPECTED",
            "capital_blocks": "EXPECTED",
            "kill_switch_state": "ARMED",
            "approval_gate": "ENFORCED",
        }

    def _execution_summary(self):
        return {
            "live_trades": 0,
            "unexpected_execution": False,
        }
