# tests/test_promotion_runner.py
import json
from pathlib import Path
import tempfile
from promotion.runner import PromotionRunner

def test_run_from_dict_promotes_and_writes_artifact(tmp_path):
    # Rules: promote if trades >= 5 and win_rate >= 0.5
    rules = {"mode": "and", "min_trades": 5, "win_rate": 0.5}
    audit_file = tmp_path / "audit.jsonl"
    artifacts_dir = tmp_path / "promoted"
    runner = PromotionRunner(rules=rules, audit_path=str(audit_file), artifacts_dir=str(artifacts_dir))
    backtest_results = {
        "good-strat": {"trades": 10, "win_rate": 0.6, "sharpe": 1.0},
        "bad-strat": {"trades": 2, "win_rate": 0.4, "sharpe": 0.2},
    }
    summary = runner.run_from_dict(backtest_results, promote_on_decision=True)
    assert summary["n_evaluated"] == 2
    assert summary["n_promoted"] == 1
    assert summary["n_demoted"] == 1
    # artifact for good-strat should exist
    p = artifacts_dir / "good-strat.json"
    assert p.exists()
    j = json.loads(p.read_text())
    assert j["strategy_id"] == "good-strat"
    assert "promoted_at" in j

def test_run_from_jsonl_reads_and_evaluates(tmp_path):
    rules = {"mode": "and", "min_trades": 1, "win_rate": 0.5}
    audit_file = tmp_path / "audit2.jsonl"
    artifacts_dir = tmp_path / "promoted2"
    runner = PromotionRunner(rules=rules, audit_path=str(audit_file), artifacts_dir=str(artifacts_dir))
    jsonl_file = tmp_path / "input.jsonl"
    with open(jsonl_file, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"strategy_id": "s1", "metrics": {"trades":5, "win_rate":0.6}}) + "\n")
        fh.write(json.dumps({"strategy_id": "s2", "metrics": {"trades":1, "win_rate":0.4}}) + "\n")
    summary = runner.run_from_jsonl(str(jsonl_file), promote_on_decision=False)
    assert summary["n_evaluated"] == 2
    assert summary["n_promoted"] == 1
    assert summary["results"]["s1"]["decision"] == "promote"
    assert summary["results"]["s2"]["decision"] == "demote"
