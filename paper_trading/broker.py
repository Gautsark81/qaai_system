# qaai_system/paper_trading/broker.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from qaai_system.backtester.noise_models import NoiseModels


@dataclass
class Position:
    qty: int = 0
    avg_cost: float = 0.0
    highest_price_seen: float = 0.0  # for trailing stops (long)
    lowest_price_seen: float = float("inf")  # for trailing short (not used currently)


@dataclass
class Trade:
    symbol: str
    side: str
    qty: int
    fill_price: float
    notional: float
    realized_pnl: float


@dataclass
class Bracket:
    """StopLoss / TakeProfit / Trailing (long only for trailing_pct)."""

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_pct: Optional[float] = None  # e.g., 0.05 for 5%

    def compute_trailing_stop(self, highest: float) -> Optional[float]:
        if self.trailing_pct is None:
            return None
        return highest * (1.0 - self.trailing_pct)


class PaperBroker:
    """
    Paper broker with:
      - spread / slippage / latency-aware market fills
      - portfolio risk controls: max drawdown, max positions, exposure cap
      - bracket orders: StopLoss, TakeProfit, Trailing stop (long)
    """

    def __init__(
        self,
        starting_cash: float = 100_000.0,
        slippage_bps: int = 5,
        spread_bps: int = 10,
        max_drawdown_pct: float = 0.2,  # 20%
        max_positions: int = 10,
        max_exposure_pct: float = 1.0,  # 100% of equity
    ):
        self.cash = float(starting_cash)
        self.slippage_bps = int(slippage_bps)
        self.spread_bps = int(spread_bps)

        # portfolio controls
        self.max_drawdown_pct = float(max_drawdown_pct)
        self.max_positions = int(max_positions)
        self.max_exposure_pct = float(max_exposure_pct)

        # state
        self.positions: Dict[str, Position] = {}
        self.brackets: Dict[str, Bracket] = {}
        self.trades: List[Trade] = []
        self.realized_pnl: float = 0.0

        # equity tracking
        self._peak_equity: float = self.cash
        self.trading_halted: bool = False

    # ---------- pricing & equity ----------
    def _market_fill_price(self, mid_price: float, side: str) -> float:
        bid, ask = NoiseModels.add_spread(mid_price, self.spread_bps)
        px = ask if side.upper() == "BUY" else bid
        px = float(NoiseModels.add_slippage(px, self.slippage_bps))
        _ = NoiseModels.latency_ms()  # sampled, not used further
        return float(px)

    def equity(self, mid_prices: Dict[str, float]) -> float:
        mtm = 0.0
        for sym, pos in self.positions.items():
            mid = float(mid_prices.get(sym, pos.avg_cost))
            mtm += pos.qty * mid
        return self.cash + mtm

    def _update_drawdown(self, equity_now: float):
        if equity_now > self._peak_equity:
            self._peak_equity = equity_now
        dd = (
            0.0
            if self._peak_equity <= 0
            else (self._peak_equity - equity_now) / self._peak_equity
        )
        if dd >= self.max_drawdown_pct:
            self.trading_halted = True

    def _current_exposure_value(self, mid_prices: Dict[str, float]) -> float:
        exp = 0.0
        for sym, pos in self.positions.items():
            mid = float(mid_prices.get(sym, pos.avg_cost))
            exp += pos.qty * mid
        return exp

    def _can_open_new(
        self, symbol: str, proposed_notional: float, mid_prices: Dict[str, float]
    ) -> Tuple[bool, str]:
        if self.trading_halted:
            return (False, "trading halted due to drawdown")

        open_syms = sum(1 for p in self.positions.values() if p.qty > 0)
        if symbol not in self.positions and open_syms >= self.max_positions:
            return (False, "max positions reached")

        eq = self.equity(mid_prices)
        if eq <= 0:
            return (False, "non-positive equity")
        current_exp = self._current_exposure_value(mid_prices)
        post_exp = current_exp + proposed_notional
        if (post_exp / eq) > self.max_exposure_pct:
            return (False, "exposure cap exceeded")

        return (True, "")

    # ---------- public: open/close ----------
    def open_long(
        self,
        symbol: str,
        mid_price: float,
        qty: int,
        mid_prices_view: Dict[str, float],
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_pct: Optional[float] = None,
    ) -> Trade:
        qty = int(qty)
        if qty <= 0:
            raise ValueError("qty must be > 0")

        preview_fill = self._market_fill_price(mid_price, "BUY")
        notional = preview_fill * qty
        can, reason = self._can_open_new(symbol, notional, mid_prices_view)
        if not can:
            raise ValueError(f"cannot open new position: {reason}")
        if notional > self.cash:
            raise ValueError("insufficient cash")

        # execute
        fill = preview_fill
        self.cash -= fill * qty
        pos = self.positions.get(symbol, Position())
        new_qty = pos.qty + qty
        new_avg = (pos.avg_cost * pos.qty + fill * qty) / new_qty
        highest_seen = max(pos.highest_price_seen, fill) if new_qty > 0 else fill
        self.positions[symbol] = Position(
            qty=new_qty, avg_cost=new_avg, highest_price_seen=highest_seen
        )

        # attach/update bracket (replaces previous)
        self.brackets[symbol] = Bracket(
            stop_loss=stop_loss, take_profit=take_profit, trailing_pct=trailing_pct
        )

        tr = Trade(symbol, "BUY", qty, fill, fill * qty, 0.0)
        self.trades.append(tr)
        return tr

    def close_long(
        self, symbol: str, mid_price: float, qty: Optional[int] = None
    ) -> Trade:
        pos = self.positions.get(symbol, Position())
        if pos.qty <= 0:
            raise ValueError("no long position to close")
        if qty is None:
            qty = pos.qty
        qty = int(qty)
        if qty <= 0 or qty > pos.qty:
            raise ValueError("invalid qty to close")

        fill = self._market_fill_price(mid_price, "SELL")
        notional = fill * qty
        realized = (fill - pos.avg_cost) * qty

        self.cash += notional
        self.realized_pnl += realized

        new_qty = pos.qty - qty
        if new_qty == 0:
            # fully closed -> remove position and brackets (OCO)
            self.positions.pop(symbol, None)
            self.brackets.pop(symbol, None)
        else:
            self.positions[symbol] = Position(
                qty=new_qty,
                avg_cost=pos.avg_cost,
                highest_price_seen=pos.highest_price_seen,
            )

        tr = Trade(symbol, "SELL", qty, fill, notional, realized)
        self.trades.append(tr)
        return tr

    # ---------- tick update: evaluate SL/TP/TRAIL ----------
    def update_prices(self, mid_prices: Dict[str, float]):
        """
        Call on each new bar/tick: adjusts trailing stops and executes SL/TP/TRAIL exits.
        """
        # update highest seen for longs
        for sym, pos in list(self.positions.items()):
            if pos.qty <= 0:
                continue
            mid = float(mid_prices.get(sym, pos.avg_cost))
            if mid > pos.highest_price_seen:
                pos.highest_price_seen = mid
                self.positions[sym] = pos

        # evaluate exits
        for sym, pos in list(self.positions.items()):
            if pos.qty <= 0:
                continue
            mid = float(mid_prices.get(sym, pos.avg_cost))
            br = self.brackets.get(sym, Bracket())

            trailing_stop = br.compute_trailing_stop(
                self.positions[sym].highest_price_seen
            )

            exit_reason = None
            # SL priority over TP if both equal/triggering
            if br.stop_loss is not None and mid <= br.stop_loss:
                exit_reason = "SL"
            elif trailing_stop is not None and mid <= trailing_stop:
                exit_reason = "TRAIL"
            elif br.take_profit is not None and mid >= br.take_profit:
                exit_reason = "TP"

            if exit_reason:
                # execute market exit for full qty
                self.close_long(sym, mid, qty=pos.qty)

        # update drawdown and possibly halt trading
        eq = self.equity(mid_prices)
        self._update_drawdown(eq)

    # ---------- convenience bracket helpers (OCO API) ----------
    def bracket_buy(
        self,
        symbol: str,
        mid_price: float,
        qty: int,
        mid_prices_view: Dict[str, float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
        trailing_pct: Optional[float] = None,
    ) -> Trade:
        """Place a market buy with bracket orders attached (stop, take-profit, optional trailing)."""
        return self.open_long(
            symbol,
            mid_price,
            qty,
            mid_prices_view,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_pct=trailing_pct,
        )

    def bracket_sell(
        self,
        symbol: str,
        mid_price: float,
        qty: int,
        mid_prices_view: Dict[str, float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
        trailing_pct: Optional[float] = None,
    ) -> Trade:
        """
        For symmetry; currently behaves same as open_long + attach bracket.
        (Short-selling not implemented here; this mirrors long bracket behavior.)
        """
        return self.open_long(
            symbol,
            mid_price,
            qty,
            mid_prices_view,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_pct=trailing_pct,
        )

    # ---------- legacy API compatibility ----------
    def market_buy(self, symbol: str, mid_price: float, qty: int):
        return self.open_long(
            symbol, mid_price, qty, mid_prices_view={symbol: mid_price}
        )

    def market_sell(self, symbol: str, mid_price: float, qty: int):
        # sells everything by default in new API if qty omitted -- keep explicit
        return self.close_long(symbol, mid_price, qty=qty)

    def position(self, symbol: str):
        """Legacy alias: returns Position or a dummy with qty=0 if flat."""
        pos = self.positions.get(symbol)
        if pos is None:

            class _FlatPos:
                qty = 0

            return _FlatPos()
        return pos
