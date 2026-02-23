# qaai_system/execution/position_manager.py
from __future__ import annotations
from typing import Dict, List, Optional
from collections import defaultdict


class PositionManager:
    """
    Tracks per-symbol positions, cost basis and computes realized + unrealized PnL.

    Supports two accounting modes:
      - 'fifo'  : First-In-First-Out lot matching (default, more precise)
      - 'avg'   : Average-cost accounting (simpler)

    Public API:
      - on_fill(symbol, side, qty, price) -> realized_pnl (float, this fill only)
      - get_position(symbol, market_price=None) -> dict with qty, avg_cost, realized_pnl, unrealized_pnl
      - get_all_positions() -> mapping symbol -> qty
      - update_market_price(symbol, price)
      - realized(symbol=None) -> per-symbol or total realized PnL
      - realized_total() -> float, across all symbols
    """

    def __init__(self, method: str = "fifo"):
        assert method in ("fifo", "avg"), "method must be 'fifo' or 'avg'"
        self.method = method
        self._lots: Dict[str, List[Dict[str, float]]] = defaultdict(list)
        self._realized: Dict[str, float] = defaultdict(float)
        self._last_price: Dict[str, float] = {}

    # ----------------- Public API -----------------

    def on_fill(self, symbol: str, side: str, qty: int, price: float) -> float:
        """
        Register a fill and return realized PnL attributable to this fill.
        """
        side = str(side).lower()
        qty = int(qty)
        price = float(price)
        if qty <= 0:
            return 0.0

        if self.method == "fifo":
            realized = (
                self._fifo_buy(symbol, qty, price)
                if side == "buy"
                else self._fifo_sell(symbol, qty, price)
            )
        else:  # avg
            realized = (
                self._avg_buy(symbol, qty, price)
                if side == "buy"
                else self._avg_sell(symbol, qty, price)
            )

        self._last_price[symbol] = price
        return float(realized)

    def get_position(
        self, symbol: str, market_price: Optional[float] = None
    ) -> Dict[str, float]:
        qty = self._net_qty(symbol)
        realized = float(self._realized.get(symbol, 0.0))
        mp = market_price if market_price is not None else self._last_price.get(symbol)

        avg_cost = self._compute_avg_cost(symbol, qty) if qty != 0 else None

        unreal = 0.0
        if mp is not None and qty != 0:
            for lot in self._lots.get(symbol, []):
                unreal += (mp - lot["price"]) * lot["qty"]

        return {
            "qty": int(qty),
            "avg_cost": float(avg_cost) if avg_cost is not None else None,
            "realized_pnl": realized,
            "unrealized_pnl": float(unreal),
        }

    def get_all_positions(self) -> Dict[str, int]:
        return {s: int(self._net_qty(s)) for s in self._lots.keys()}

    def update_market_price(self, symbol: str, price: float) -> None:
        self._last_price[symbol] = float(price)

    # ----------------- Realized PnL API -----------------

    def realized(self, symbol: Optional[str] = None) -> float:
        """Return realized PnL for a given symbol (or total if None)."""
        if symbol is None:
            return float(sum(self._realized.values()))
        return float(self._realized.get(symbol, 0.0))

    def realized_total(self) -> float:
        """Return total realized PnL across all symbols (alias for tests)."""
        return float(sum(self._realized.values()))

    def realized_pnl(self, method: str = "fifo") -> float:
        """
        Compatibility wrapper: return realized PnL across all symbols.
        Some tests call realized_pnl(method="fifo").
        """
        if method != "fifo":
            raise NotImplementedError(f"realized_pnl method '{method}' not implemented")
        return self.realized_total()

    # ----------------- Internals - FIFO -----------------

    def _fifo_buy(self, symbol: str, qty: int, price: float) -> float:
        realized = 0.0
        lots = self._lots[symbol]

        i = 0
        while qty > 0 and i < len(lots):
            lot = lots[i]
            if lot["qty"] >= 0:
                break
            available = -lot["qty"]
            cover = min(qty, available)
            realized += (lot["price"] - price) * cover
            lot["qty"] += cover
            qty -= cover
            if lot["qty"] == 0:
                lots.pop(i)
            else:
                i += 1

        if qty > 0:
            lots.append({"qty": qty, "price": price})

        self._realized[symbol] += realized
        return realized

    def _fifo_sell(self, symbol: str, qty: int, price: float) -> float:
        realized = 0.0
        lots = self._lots[symbol]

        i = 0
        while qty > 0 and i < len(lots):
            lot = lots[i]
            if lot["qty"] <= 0:
                i += 1
                continue
            available = lot["qty"]
            take = min(qty, available)
            realized += (price - lot["price"]) * take
            lot["qty"] -= take
            qty -= take
            if lot["qty"] == 0:
                lots.pop(i)
            else:
                i += 1

        if qty > 0:
            lots.append({"qty": -qty, "price": price})

        self._realized[symbol] += realized
        return realized

    # ----------------- Internals - AVG -----------------

    def _avg_buy(self, symbol: str, qty: int, price: float) -> float:
        cur_qty = self._net_qty(symbol)
        cur_avg = self._compute_avg_cost(symbol, cur_qty) if cur_qty != 0 else 0.0
        realized = 0.0

        if cur_qty < 0:
            cover = min(qty, -cur_qty)
            realized += (cur_avg - price) * cover
            qty -= cover
            self._lots[symbol] = []
            if qty > 0:
                self._lots[symbol].append({"qty": qty, "price": price})
        else:
            total_qty = cur_qty + qty
            if total_qty == 0:
                self._lots[symbol] = []
            else:
                base_notional = cur_qty * cur_avg
                new_notional = base_notional + qty * price
                new_avg = new_notional / total_qty
                self._lots[symbol] = [{"qty": total_qty, "price": new_avg}]

        self._realized[symbol] += realized
        return realized

    def _avg_sell(self, symbol: str, qty: int, price: float) -> float:
        cur_qty = self._net_qty(symbol)
        cur_avg = self._compute_avg_cost(symbol, cur_qty) if cur_qty != 0 else 0.0
        realized = 0.0

        if cur_qty > 0:
            cover = min(qty, cur_qty)
            realized += (price - cur_avg) * cover
            qty -= cover
            remaining = cur_qty - cover
            if remaining > 0:
                self._lots[symbol] = [{"qty": remaining, "price": cur_avg}]
            else:
                self._lots[symbol] = []
            if qty > 0:
                self._lots[symbol].append({"qty": -qty, "price": price})
        else:
            if cur_qty < 0:
                total_short = -cur_qty + qty
                new_avg = (
                    ((-cur_qty) * cur_avg + qty * price) / total_short
                    if total_short != 0
                    else price
                )
                self._lots[symbol] = [{"qty": -total_short, "price": new_avg}]
            else:
                self._lots[symbol] = [{"qty": -qty, "price": price}]

        self._realized[symbol] += realized
        return realized

    # ----------------- Helpers -----------------

    def _net_qty(self, symbol: str) -> int:
        return sum(l["qty"] for l in self._lots.get(symbol, []))

    def _compute_avg_cost(
        self, symbol: str, net_qty: Optional[int] = None
    ) -> Optional[float]:
        lots = self._lots.get(symbol, [])
        if not lots:
            return None
        if net_qty is None:
            net_qty = self._net_qty(symbol)
        if net_qty == 0:
            return None

        if net_qty > 0:
            notional = sum(l["qty"] * l["price"] for l in lots if l["qty"] > 0)
            qty = sum(l["qty"] for l in lots if l["qty"] > 0)
            return notional / qty if qty else None
        else:
            notional = sum((-l["qty"]) * l["price"] for l in lots if l["qty"] < 0)
            qty = sum(-l["qty"] for l in lots if l["qty"] < 0)
            return notional / qty if qty else None

    # ----------------- Diagnostics -----------------

    def lots(self, symbol: str) -> List[Dict[str, float]]:
        return [dict(l) for l in self._lots.get(symbol, [])]

    def last_price(self, symbol: str) -> Optional[float]:
        return self._last_price.get(symbol)
