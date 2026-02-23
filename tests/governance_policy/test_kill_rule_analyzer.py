from modules.governance_policy.kill_rule_analyzer import KillRuleAnalyzer
from modules.governance_feedback.kill_attribution import (
    KillAttribution,
    KillReason,
)


def test_kill_rule_analyzer():
    kills = [
        KillAttribution("s1", KillReason.DRAWDOWN, ""),
        KillAttribution("s2", KillReason.DRAWDOWN, ""),
        KillAttribution("s3", KillReason.SSR_DECAY, ""),
    ]

    stats = KillRuleAnalyzer().analyze(kills)

    assert stats[KillReason.DRAWDOWN] == 2
