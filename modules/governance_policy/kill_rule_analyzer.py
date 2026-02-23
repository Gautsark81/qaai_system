from typing import List, Dict
from collections import Counter
from modules.governance_feedback.kill_attribution import KillAttribution


class KillRuleAnalyzer:
    def analyze(self, kills: List[KillAttribution]) -> Dict[str, int]:
        """
        Returns kill_reason -> frequency
        """
        return dict(Counter(k.reason for k in kills))
