# tests/test_promotion_engine.py
import json
import os
from pathlib import Path
import tempfile
from promotion.engine import PromotionEngine

SIMPLE_CFG = {
    "defaults": {"min_trades": 10, "max_drawdown_abs": 0.4},
    "rules": [
        {"name": "promo1", "priority": 10, "action": "PROMOTE",
         "conditions": {"win_rate": {">=": 0.6}, "pf": {">=": 1.5}, "trades": {">=": 20}}},
        {"name": "demote_pf", "priority": 5, "action": "DEMOTE",
         "conditions": {"pf": {"<": 1.0}}},
    ]
}

def test_promote_match():
    eng = PromotionEngine(SIMPLE_CFG)
    metrics = {"win_rate": 0.62, "pf": 1.6, "trades": 30, "drawdown": 0.1}
    d = eng.evaluate(metrics)
    assert d["decision"] == "PROMOTE"
    assert d["matched_rule"] == "promo1"

def test_demote_by_pf():
    eng = PromotionEngine(SIMPLE_CFG)
    metrics = {"win_rate": 0.4, "pf": 0.95, "trades": 50}
    d = eng.evaluate(metrics)
    assert d["decision"] == "DEMOTE"
    assert "pf" in d["reason"]

def test_hold_when_no_rules():
    eng = PromotionEngine({"defaults": {"min_trades": 5}})
    metrics = {"win_rate": 0.5, "pf": 1.1, "trades": 6}
    d = eng.evaluate(metrics)
    assert d["decision"] == "HOLD"
    
def test_promote_when_metrics_meet_thresholds(tmp_path):
    rules = {"mode": "and", "min_trades": 10, "win_rate": 0.5, "sharpe": 0.5}
    audit_file = tmp_path / "audit.jsonl"
    engine = PromotionEngine(rules=rules, audit_path=str(audit_file))

    metrics = {"trades": 15, "win_rate": 0.55, "sharpe": 0.7}
    res = engine.evaluate("s1", metrics)
    assert res["decision"] == "promote"
    # audit file should contain one JSON line with decision promote
    text = audit_file.read_text()
    j = json.loads(text.strip().splitlines()[-1])
    assert j["strategy_id"] == "s1"
    assert j["decision"] == "promote"

def test_demote_when_metrics_fail(tmp_path):
    rules = {"mode": "and", "min_trades": 20, "win_rate": 0.6}
    audit_file = tmp_path / "audit2.jsonl"
    engine = PromotionEngine(rules=rules, audit_path=str(audit_file))

    metrics = {"trades": 10, "win_rate": 0.55}
    res = engine.evaluate("s2", metrics)
    assert res["decision"] == "demote"
    j = json.loads(audit_file.read_text().strip().splitlines()[-1])
    assert j["strategy_id"] == "s2"
    assert j["decision"] == "demote"

def test_missing_metrics_leads_to_demote_and_audit(tmp_path):
    rules = {"mode": "and", "min_trades": 1, "win_rate": 0.5}
    audit_file = tmp_path / "audit3.jsonl"
    engine = PromotionEngine(rules=rules, audit_path=str(audit_file))

    metrics = {"trades": 5}  # missing win_rate
    res = engine.evaluate("s3", metrics, extra={"note": "test"})
    assert res["decision"] == "demote"
    j = json.loads(audit_file.read_text().strip().splitlines()[-1])
    assert "missing metric win_rate" in j["reason"] or "win_rate" in j["reason"]
