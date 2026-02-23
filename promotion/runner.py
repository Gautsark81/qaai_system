# promotion/runner.py
"""
PromotionRunner: evaluates runs (via simple rules or PromotionEngine) and writes audit + promoted artifacts.

Constructor expected by tests:
    PromotionRunner(rules=..., audit_path=str(audit_file), artifacts_dir=str(artifacts_dir))
"""
from __future__ import annotations
from typing import Dict, Any, Optional, Union
import logging
import json
import uuid
from pathlib import Path
import datetime

from promotion.engine import PromotionEngine
from promotion.audit import AuditWriter

logger = logging.getLogger(__name__)


class PromotionRunner:
    """
    Runner that wires simple rule evaluation (when rules provided) or PromotionEngine otherwise,
    writes audit JSONL lines, and writes promoted artifacts (deterministic filenames).
    """
    def __init__(self,
                 *,
                 rules: Optional[Dict[str, Any]] = None,
                 audit_path: Optional[str] = "promotion/demo_audit.jsonl",
                 artifacts_dir: Optional[str] = "promotion/promoted",
                 engine_config: Optional[Dict[str, Any]] = None):
        # store inputs
        self.rules = rules or {}
        self.audit_path = Path(audit_path) if audit_path else None
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else None

        # ensure directories exist
        if self.audit_path:
            try:
                self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.exception("Failed to create audit directory %s", self.audit_path)

        if self.artifacts_dir:
            try:
                self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.exception("Failed to create artifacts directory %s", self.artifacts_dir)

        # prepare engine and audit writer (engine may be unused if rules provided)
        engine_cfg = engine_config or {}
        if self.rules:
            engine_cfg = {**engine_cfg, "rules": self.rules}
        self.engine = PromotionEngine(engine_cfg)
        self.audit = AuditWriter(str(self.audit_path)) if self.audit_path else None

    # -------------------------
    # Helpers
    # -------------------------
    def _format_decision_str(self, promoted: bool) -> str:
        return "promote" if promoted else "demote"

    def _sanitize_filename(self, name: str) -> str:
        """Make a filesystem-safe filename base from a strategy id."""
        s = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(name))
        if not s:
            s = str(uuid.uuid4())
        return s

    def _utc_now_iso(self) -> str:
        """Return current UTC time in ISO 8601 format."""
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    # -------------------------
    # Core processing
    # -------------------------
    def process(self, strategy_id: str, metrics: Dict[str, Any], extra: Optional[Dict[str, Any]] = None, promote: bool = True) -> Dict[str, Any]:
        """
        Evaluate metrics for strategy_id using rules (if provided) or PromotionEngine otherwise.
        Append an audit entry and, if promoted and promote==True, write an artifact file named
        <sanitized_strategy_id>.json into artifacts_dir.

        Returns a dict: {"decision": bool, "matched_rule": ..., "metrics": ...}
        """
        # 1) rule-based evaluation (tests expect this behavior when rules are passed)
        decision_flag: Optional[bool] = None
        matched_rule = None

        if self.rules:
            mode = self.rules.get("mode", "and")
            checks = []

            if "min_trades" in self.rules:
                try:
                    checks.append(int(metrics.get("trades", 0)) >= int(self.rules["min_trades"]))
                except Exception:
                    checks.append(False)

            if "win_rate" in self.rules:
                try:
                    checks.append(float(metrics.get("win_rate", 0.0)) >= float(self.rules["win_rate"]))
                except Exception:
                    checks.append(False)

            if mode == "and":
                decision_flag = all(checks)
            else:
                decision_flag = any(checks)

            matched_rule = self.rules

        # 2) fallback to engine
        if decision_flag is None:
            try:
                engine_decision = self.engine.evaluate(strategy_id, metrics, extra=extra)
                decision_flag = bool(engine_decision.get("decision"))
                matched_rule = engine_decision.get("matched_rule")
            except Exception:
                logger.exception("PromotionEngine.evaluate failed; defaulting decision to False for %s", strategy_id)
                decision_flag = False
                matched_rule = None

        # 3) audit entry
        audit_entry = {
            "strategy_id": strategy_id,
            "decision": decision_flag,
            "matched_rule": matched_rule,
            "metrics": metrics,
        }
        if extra:
            audit_entry["extra"] = extra

        # 4) write artifact if promoted and allowed
        if decision_flag and promote and self.artifacts_dir:
            try:
                safe_name = self._sanitize_filename(strategy_id)
                artifact_filename = f"{safe_name}.json"
                artifact_path = self.artifacts_dir / artifact_filename
                # deterministic filename (overwrite allowed)
                artifact_payload = {
                    "strategy_id": strategy_id,
                    "metrics": metrics,
                    "extra": extra,
                    "promoted_at": self._utc_now_iso(),
                }
                with open(artifact_path, "w", encoding="utf-8") as fh:
                    json.dump(artifact_payload, fh, ensure_ascii=False, indent=2)
                audit_entry["artifact"] = artifact_filename
            except Exception:
                logger.exception("Failed to write artifact for promoted strategy %s", strategy_id)

        # 5) append audit JSONL
        if self.audit:
            try:
                self.audit.append(audit_entry)
            except Exception:
                logger.exception("AuditWriter.append failed; falling back to direct append")
                try:
                    if self.audit_path:
                        with open(self.audit_path, "a", encoding="utf-8") as ah:
                            ah.write(json.dumps(audit_entry) + "\n")
                except Exception:
                    logger.exception("Fallback audit append failed for %s", strategy_id)
        else:
            if self.audit_path:
                try:
                    with open(self.audit_path, "a", encoding="utf-8") as ah:
                        ah.write(json.dumps(audit_entry) + "\n")
                except Exception:
                    logger.exception("Failed to append audit jsonl fallback for %s", strategy_id)

        return {"decision": decision_flag, "matched_rule": matched_rule, "metrics": metrics}

    # -------------------------
    # Bulk helpers matching test expectations
    # -------------------------
    def run_from_dict(self, run_or_runs: Union[Dict[str, Any], Dict[str, Dict[str, Any]]], promote_on_decision: bool = True) -> Dict[str, Any]:
        """
        Accept either:
          - mapping strategy_id -> metrics (multi-run),
          - single run dict with 'strategy_id'/'id' or metrics.

        Returns summary shaped for tests:
        {
            "n_evaluated": int,
            "n_promoted": int,
            "n_demoted": int,
            "results": {
                "<strategy_id>": {"decision": "promote"|"demote", "metrics": {...}, "artifact": optional}
            }
        }
        """
        # heuristic to detect multi-run mapping
        is_multi = False
        if isinstance(run_or_runs, dict):
            metric_keys = {"trades", "win_rate", "wins", "metrics", "sharpe", "pnl"}
            if all(isinstance(v, dict) for v in run_or_runs.values()) and not metric_keys.intersection(set(run_or_runs.keys())):
                is_multi = True

        results: Dict[str, Any] = {}
        n_evaluated = 0
        n_promoted = 0

        if is_multi:
            for strategy_id, metrics in run_or_runs.items():
                n_evaluated += 1
                decision = self.process(strategy_id, metrics, extra=None, promote=promote_on_decision)
                promoted = bool(decision.get("decision"))
                if promoted:
                    n_promoted += 1

                entry: Dict[str, Any] = {
                    "decision": self._format_decision_str(promoted),
                    "metrics": metrics
                }
                if promoted and promote_on_decision and self.artifacts_dir:
                    try:
                        safe_name = self._sanitize_filename(strategy_id)
                        entry["artifact"] = f"{safe_name}.json"
                    except Exception:
                        pass

                results[str(strategy_id)] = entry
        else:
            # treat as single-run dict
            run = run_or_runs
            strategy_id = run.get("strategy_id") or run.get("id") or f"run-{uuid.uuid4()}"
            metrics = run.get("metrics") if isinstance(run.get("metrics"), dict) else {k: v for k, v in run.items() if k not in {"strategy_id", "id"}}
            n_evaluated = 1
            decision = self.process(strategy_id, metrics, extra=None, promote=promote_on_decision)
            promoted = bool(decision.get("decision"))
            n_promoted = 1 if promoted else 0

            entry = {
                "decision": self._format_decision_str(promoted),
                "metrics": metrics
            }
            if promoted and promote_on_decision and self.artifacts_dir:
                try:
                    safe_name = self._sanitize_filename(strategy_id)
                    entry["artifact"] = f"{safe_name}.json"
                except Exception:
                    pass

            results[str(strategy_id)] = entry

        n_demoted = n_evaluated - n_promoted
        return {
            "n_evaluated": n_evaluated,
            "n_promoted": n_promoted,
            "n_demoted": n_demoted,
            "results": results
        }

    def run_from_jsonl(self, jsonl_path: str, promote_on_decision: bool = True) -> Dict[str, Any]:
        """
        Read JSONL file, normalize into mapping strategy_id->metrics, and delegate to run_from_dict.
        """
        p = Path(jsonl_path)
        if not p.exists():
            raise FileNotFoundError(f"{jsonl_path} not found")

        runs_map: Dict[str, Dict[str, Any]] = {}
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    run = json.loads(line)
                except json.JSONDecodeError:
                    fake_id = f"malformed-{uuid.uuid4()}"
                    runs_map[fake_id] = {"_error": "malformed_json", "raw": line}
                    continue

                strategy_id = run.get("strategy_id") or run.get("id") or f"run-{uuid.uuid4()}"
                metrics = run.get("metrics") if isinstance(run.get("metrics"), dict) else {k: v for k, v in run.items() if k not in {"strategy_id", "id"}}
                runs_map[strategy_id] = metrics

        return self.run_from_dict(runs_map, promote_on_decision=promote_on_decision)
