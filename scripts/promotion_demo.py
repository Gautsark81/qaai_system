# scripts/promotion_demo.py
"""
Small CLI demo to run the promotion runner against a synthetic metrics example.
"""
import json
from promotion.runner import PromotionRunner

DEFAULT_CONFIG = {
    "defaults": {"min_trades": 20, "max_drawdown_abs": 0.35},
    "rules": [
        {"name": "fast_promote", "priority": 10, "action": "PROMOTE",
         "conditions": {"win_rate": {">=": 0.6}, "pf": {">=": 1.6}, "trades": {">=": 50}}},
        {"name": "stable_promote", "priority": 8, "action": "PROMOTE", "allow_low_trades": False,
         "conditions": {"win_rate": {">=": 0.55}, "pf": {">=": 1.4}, "sharpe": {">=": 1.2}, "trades": {">=": 100}}},
        {"name": "demote_on_pf", "priority": 5, "action": "DEMOTE",
         "conditions": {"pf": {"<": 1.0}}},
    ]
}

def main():
    runner = PromotionRunner(DEFAULT_CONFIG, audit_path="promotion/demo_audit.jsonl")
    # synthetic metrics
    metrics = {
        "win_rate": 0.62,
        "pf": 1.7,
        "sharpe": 1.3,
        "trades": 75,
        "drawdown": 0.12,
    }
    decision = runner.process("example_strategy_v1", metrics, extra={"run_id": "demo-001"})
    print(json.dumps(decision, indent=2))

if __name__ == "__main__":
    main()
