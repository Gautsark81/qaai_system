# infra/live_pnl.py
"""
Live PnL streamer: small helper to create a snapshot dict with account NAV and positions.
Not a background task — call get_snapshot() when you need a current view.
"""

from typing import Dict, Any


class LivePnL:
    def __init__(self, provider, price_lookup=None):
        """
        provider: UnifiedProvider or provider implementing get_account_nav() and get_positions()
        price_lookup: callable(symbol) -> price (used for unrealized). If None, unrealized will be 0.
        """
        self.provider = provider
        self.price_lookup = price_lookup

    def get_snapshot(self) -> Dict[str, Any]:
        nav = None
        try:
            nav = self.provider.get_account_nav()
        except Exception:
            nav = None
        try:
            pos = self.provider.get_positions()
        except Exception:
            pos = {}
        # compute naive unrealized
        unreal = {}
        for s, q in (pos or {}).items():
            try:
                price = self.price_lookup(s) if self.price_lookup is not None else None
            except Exception:
                price = None
            if price is not None:
                unreal[s] = price * q
            else:
                unreal[s] = 0.0
        return {"account_nav": nav, "positions": pos, "unreal_value": unreal}
