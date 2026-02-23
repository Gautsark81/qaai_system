import argparse
from modules.governance.approval import ApprovalService
from modules.governance.approval_store import ApprovalStore
from modules.governance.decision_log import (
    GovernanceDecision,
    GovernanceDecisionLog,
)
from datetime import datetime


def approve_strategy_cli():
    parser = argparse.ArgumentParser("qaai-approve")
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--ttl", type=int, default=72)
    parser.add_argument("--reason", required=True)

    args = parser.parse_args()

    svc = ApprovalService()
    store = ApprovalStore()
    log = GovernanceDecisionLog()

    record = svc.approve(
        strategy_id=args.strategy,
        approver=args.approver,
        reason=args.reason,
        ttl_hours=args.ttl,
    )

    store.save(record)

    log.record(
        GovernanceDecision(
            strategy_id=args.strategy,
            decision="APPROVED",
            actor=args.approver,
            timestamp=datetime.utcnow(),
            reason=args.reason,
        )
    )

    print(f"Strategy {args.strategy} APPROVED until {record.expires_at}")
