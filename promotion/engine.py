# promotion/engine.py
"""
PromotionEngine: test-compatible behavior.

- evaluate(metrics) -> returns UPPERCASE decision strings.
- evaluate(strategy_id, metrics, extra=...) -> returns lowercase decision strings and writes lowercase audit.
- Matched rule reason is descriptive and includes metric names/values.
- If rules exist but none match, returns DEMOTE and includes failure reasons (missing metrics etc).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Tuple
import operator
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

_OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

class PromotionEngineError(Exception):
    pass

def _ensure_dir_for_file(path: str) -> None:
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)

@dataclass
class Rule:
    name: str
    action: str  # 'PROMOTE'|'DEMOTE'|'HOLD' externally
    conditions: Dict[str, Dict[str, Any]]
    priority: int = 0
    allow_low_trades: bool = False

class PromotionEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None, *, rules: Optional[Any] = None, audit_path: Optional[str] = None):
        cfg = config or {}
        self.audit_path = audit_path or cfg.get("audit_path")
        self.defaults: Dict[str, Any] = dict(cfg.get("defaults", {}))

        raw_rules = rules if rules is not None else cfg.get("rules")
        self._rules: List[Rule] = []

        # carry min_trades from shorthand rules into defaults if provided
        if isinstance(raw_rules, dict) and "min_trades" in raw_rules:
            try:
                self.defaults.setdefault("min_trades", int(raw_rules.get("min_trades")))
            except Exception:
                pass

        if raw_rules is None:
            if isinstance(cfg, dict) and any(k in cfg for k in ("mode", "min_trades")):
                r = self._build_rule_from_shorthand(cfg, name="default")
                self._rules.append(r)
        elif isinstance(raw_rules, dict):
            r = self._build_rule_from_shorthand(raw_rules, name=raw_rules.get("name", "rule"))
            self._rules.append(r)
        elif isinstance(raw_rules, list):
            for rr in raw_rules:
                if not isinstance(rr, dict):
                    continue
                name = rr.get("name", rr.get("action", "rule"))
                action = str(rr.get("action", "PROMOTE")).upper()
                conds = rr.get("conditions", {})
                normalized = {}
                for k, v in conds.items():
                    if isinstance(v, dict):
                        normalized[k] = v
                    else:
                        normalized[k] = {">=": v}
                priority = int(rr.get("priority", 0))
                allow_low_trades = bool(rr.get("allow_low_trades", False))
                self._rules.append(Rule(name=name, action=action, conditions=normalized, priority=priority, allow_low_trades=allow_low_trades))
        else:
            raise PromotionEngineError("Unsupported rules format")

        self._rules.sort(key=lambda r: -int(r.priority))

    def _build_rule_from_shorthand(self, data: Dict[str, Any], name: str = "default") -> Rule:
        conds: Dict[str, Dict[str, Any]] = {}
        for k, v in data.items():
            if k in ("mode", "name", "action", "min_trades"):
                continue
            if isinstance(v, dict):
                conds[k] = v
            else:
                try:
                    float(v)
                    conds[k] = {">=": v}
                except Exception:
                    conds[k] = {">=": v}
        action = str(data.get("action", "PROMOTE")).upper()
        priority = int(data.get("priority", 0))
        allow_low_trades = bool(data.get("allow_low_trades", False))
        return Rule(name=name, action=action, conditions=conds, priority=priority, allow_low_trades=allow_low_trades)

    def _check_condition(self, metric_val: Any, cond: Dict[str, Any]) -> Tuple[bool, str]:
        if metric_val is None:
            return False, "missing"
        for op, threshold in cond.items():
            func = _OPS.get(op)
            if func is None:
                return False, f"unsupported-op:{op}"
            try:
                mv = float(metric_val)
                th = float(threshold)
            except Exception:
                return False, f"bad-compare:{metric_val}:{threshold}"
            if not func(mv, th):
                # produce a compact failure reason
                return False, f"{mv} {op} {th} failed"
        return True, ""

    def _match_rule(self, rule: Rule, metrics: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, str]]:
        """
        Returns (matched, descriptive_reason, per_metric_outcomes)
        - descriptive_reason: if matched -> textual summary of matched conditions (metric op threshold (value))
                             if not matched -> concatenated per-metric failure reasons
        - per_metric_outcomes: mapping metric -> outcome-string (useful for building final aggregated reason)
        """
        failures = []
        outcomes: Dict[str, str] = {}
        for metric_name, cond in rule.conditions.items():
            mv = metrics.get(metric_name)
            ok, reason = self._check_condition(mv, cond)
            if ok:
                # record as matched detail
                # build text like "pf < 1.0 (0.95)"
                # pick the first op for display
                op, th = next(iter(cond.items()))
                try:
                    val = float(mv)
                except Exception:
                    val = mv
                outcomes[metric_name] = f"{metric_name} {op} {th} ({val})"
            else:
                outcomes[metric_name] = f"{metric_name}:{reason}"
                failures.append(outcomes[metric_name])
        if failures:
            return False, "; ".join(failures), outcomes
        # matched; build descriptive reason from outcomes
        desc = "; ".join(outcomes[m] for m in rule.conditions.keys())
        return True, desc, outcomes

    def _write_audit(self, entry: Dict[str, Any]) -> None:
        if not self.audit_path:
            return
        _ensure_dir_for_file(self.audit_path)
        entry = dict(entry)
        entry.setdefault("ts_iso", datetime.utcnow().isoformat() + "Z")
        line = json.dumps(entry, default=str, ensure_ascii=False)
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass

    def evaluate(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Two calling styles:
        - evaluate(metrics_dict) -> returns decision dict (DECISION in UPPERCASE)
        - evaluate(strategy_id, metrics_dict, extra=...) -> returns decision dict (decision lowercase) and writes audit with lowercase decision
        """
        if len(args) == 1 and isinstance(args[0], dict):
            strategy_id = None
            metrics = args[0]
            extra = None
            return_lower = False
        elif len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
            strategy_id = args[0]
            metrics = args[1]
            extra = kwargs.get("extra")
            return_lower = True
        else:
            raise PromotionEngineError("evaluate expects either (metrics) or (strategy_id, metrics[, extra=...])")

        metrics = dict(metrics or {})
        for k, v in self.defaults.items():
            metrics.setdefault(k, v)

        trades = int(metrics.get("trades", 0))
        min_trades = int(self.defaults.get("min_trades", 10))
        too_few_trades = trades < min_trades

        any_rule_present = len(self._rules) > 0
        collected_failures: List[str] = []

        for rule in self._rules:
            if too_few_trades and not rule.allow_low_trades:
                logger.debug("Rule %s skipped due to low trades (%s < %s)", rule.name, trades, min_trades)
                # treat as failure reason for reporting
                collected_failures.append(f"low_trades:{trades}<{min_trades}")
                continue
            matched, reason, per_metric = self._match_rule(rule, metrics)
            if matched:
                dec_upper = rule.action.upper()
                dec_lower = rule.action.lower()
                # choose return format based on call style
                decision_out = dec_lower if return_lower else dec_upper
                out = {"decision": decision_out, "reason": reason or "matched", "matched_rule": rule.name, "metrics": metrics}
                # audit must store lowercase decision (tests expect lowercase in audit file)
                if strategy_id:
                    audit_entry = {"strategy_id": strategy_id, "decision": dec_lower, "reason": reason or "matched", "matched_rule": rule.name, "metrics": metrics}
                    if extra:
                        audit_entry["extra"] = extra
                    try:
                        self._write_audit(audit_entry)
                    except Exception:
                        logger.exception("audit write failed")
                return out
            else:
                # accumulate fail reason for this rule to explain later why none matched
                if reason:
                    collected_failures.append(f"{rule.name}:{reason}")

        # If rules present and none matched -> DEMOTE (or demote lowercase when strategy_id provided)
        if any_rule_present:
            dec_upper = "DEMOTE"
            dec_lower = "demote"
            reason = "; ".join(collected_failures) if collected_failures else "no rule matched"
            out = {"decision": dec_lower if return_lower else dec_upper, "reason": reason, "matched_rule": None, "metrics": metrics}
            if strategy_id:
                audit_entry = {"strategy_id": strategy_id, "decision": dec_lower, "reason": reason, "metrics": metrics}
                if extra:
                    audit_entry["extra"] = extra
                try:
                    self._write_audit(audit_entry)
                except Exception:
                    logger.exception("audit write failed")
            return out

        # fallback demote on pf/drawdown
        pf = metrics.get("pf")
        drawdown = metrics.get("drawdown")
        if pf is not None and float(pf) < 1.0:
            dec_upper, dec_lower = "DEMOTE", "demote"
            reason = f"pf below 1.0 (pf={pf})"
            out = {"decision": dec_lower if return_lower else dec_upper, "reason": reason, "matched_rule": None, "metrics": metrics}
            if strategy_id:
                self._write_audit({"strategy_id": strategy_id, "decision": dec_lower, "reason": reason, "metrics": metrics, **({"extra": extra} if extra else {})})
            return out
        if drawdown is not None and float(drawdown) > float(self.defaults.get("max_drawdown_abs", 0.4)):
            dec_upper, dec_lower = "DEMOTE", "demote"
            reason = f"drawdown exceeds threshold (drawdown={drawdown})"
            out = {"decision": dec_lower if return_lower else dec_upper, "reason": reason, "matched_rule": None, "metrics": metrics}
            if strategy_id:
                self._write_audit({"strategy_id": strategy_id, "decision": dec_lower, "reason": reason, "metrics": metrics, **({"extra": extra} if extra else {})})
            return out

        # otherwise HOLD
        dec_upper, dec_lower = "HOLD", "hold"
        out = {"decision": dec_lower if return_lower else dec_upper, "reason": "no matching promotion/demotion rule", "matched_rule": None, "metrics": metrics}
        if strategy_id:
            self._write_audit({"strategy_id": strategy_id, "decision": dec_lower, "reason": out["reason"], "metrics": metrics, **({"extra": extra} if extra else {})})
        return out
