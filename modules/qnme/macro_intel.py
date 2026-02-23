# modules/qnme/macro_intel.py
from typing import Dict, Any

class MacroIntel:
    """
    Layer 8: Long-horizon intelligence.
    For now this is a simple aggregator with placeholder connectors.
    Replace data ingestion with real feeds.
    """

    def __init__(self):
        self.latest = {}

    def update_fii_dii(self, data: Dict[str, Any]):
        self.latest["fii_dii"] = data

    def update_options_term(self, data: Dict[str, Any]):
        self.latest["options_term"] = data

    def compute_bias(self) -> Dict[str, Any]:
        """
        Return a small bias summary:
        - global_bias: -1..1 where positive = net buy bias
        - vol_profile: "low"|"med"|"high"
        """
        fii = self.latest.get("fii_dii", {})
        net = fii.get("net", 0.0)
        bias = max(-1.0, min(1.0, net / (abs(net) + 100000.0 + 1e-9)))
        vol_profile = "med"
        return {"global_bias": bias, "vol_profile": vol_profile}
