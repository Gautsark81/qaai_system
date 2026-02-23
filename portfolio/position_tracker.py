# path: qaai_system/portfolio/position_tracker.py
from __future__ import annotations

"""
PositionTracker v2.0 — hedge-fund-grade, broker-agnostic position book.

- Tracks long/short positions by symbol
- Handles partial fills and flips (long -> flat -> short, etc.)
- Maintains realized & unrealized PnL
- Produces PortfolioSnapshot for monitoring / analytics
- Provides:
    * apply_fill(...)
    * apply_fill_event(...)
    * close_position(...)
    * get_position(...)
    * get_all_positions(...)
    * get_closed_trades(...)
    * get_portfolio_snapshot(...)
    * log_snapshot(...)  (small logging helper)
"""

import threading
import time
from typing import Callable, Dict, Any, Optional, List

from .models import Position, PortfolioSnapshot

class PositionTracker:
    """
    Thread-safe position + portfolio tracker.

    Parameters
    ----------
    price_fetcher : callable, optional
        Function price_fetcher(symbol) -> float, used for unrealized PnL
        and for close_position() if available.
    logger : logging.Logger-like, optional
        Logger used by log_snapshot and debug messages.
    """
    def __init__(
        self,
        price_fetcher: Optional[Callable[[str], float]] = None,
        logger: Optional[Any] = None,
    ) -> None:
        self._lock = threading.Lock()
        self._positions: Dict[str, Position] = {}
        self._closed_trades: List[Dict[str, Any]] = []

        self._realized_pnl_total: float = 0.0
        self._price_fetcher = price_fetcher
        self._logger = logger

        # NEW: simple idempotency cache for fill events
        # (trade_id -> timestamp)
        self._applied_trade_ids: Dict[str, float] = {}
        self._trade_id_ttl_seconds: float = 60 * 60 * 6  # 6 hours window

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    def apply_fill(
        self,
        symbol: str,
        side: str,
        qty: int,
        price: float,
        fees: float = 0.0,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Apply a fill to the position book.

        Parameters
        ----------
        symbol : str
            Instrument identifier.
        side : str
            'BUY' or 'SELL' (case-insensitive).
        qty : int
            Filled quantity.
        price : float
            Fill price.
        fees : float, optional
            Fees/commissions associated with this fill.
        meta : dict, optional
            Arbitrary metadata (strategy id, order id, etc.).

        Returns
        -------
        dict
            Summary of the update:
            {
                "symbol": ...,
                "side": "LONG"/"SHORT"/None,
                "realized_pnl": float,
                "position_closed": bool,
            }
        """
        symbol = str(symbol)
        side_u = str(side).upper()
        qty = int(qty)
        price = float(price)

        if qty <= 0:
            return {
                "symbol": symbol,
                "side": None,
                "realized_pnl": 0.0,
                "position_closed": False,
            }

        if side_u not in ("BUY", "SELL"):
            raise ValueError(f"Side must be BUY/SELL, got {side}")

        meta = meta or {}

        with self._lock:
            pos = self._positions.get(symbol)

            def _realized_for(
                existing: Position, exit_side: str, exit_qty: int, exit_price: float
            ) -> float:
                if exit_qty <= 0:
                    return 0.0
                if existing.side == "LONG" and exit_side == "SELL":
                    return (exit_price - existing.avg_price) * exit_qty
                if existing.side == "SHORT" and exit_side == "BUY":
                    return (existing.avg_price - exit_price) * exit_qty
                return 0.0

            realized_pnl = 0.0
            realized_closed = False

            # No existing position -> open a new one
            if pos is None:
                new_side = "LONG" if side_u == "BUY" else "SHORT"
                pos = Position(
                    symbol=symbol,
                    side=new_side,
                    quantity=qty,
                    avg_price=price,
                    meta=dict(meta),
                )
                self._positions[symbol] = pos

            else:
                remaining_qty = qty

                # Opposite direction: close or flip
                if (pos.side == "LONG" and side_u == "SELL") or (
                    pos.side == "SHORT" and side_u == "BUY"
                ):
                    close_qty = min(pos.quantity, remaining_qty)
                    realized_pnl_delta = _realized_for(
                        existing=pos,
                        exit_side=side_u,
                        exit_qty=close_qty,
                        exit_price=price,
                    )

                    realized_pnl += realized_pnl_delta
                    pos.realized_pnl += realized_pnl_delta
                    self._realized_pnl_total += realized_pnl_delta

                    pos.quantity -= close_qty
                    remaining_qty -= close_qty

                    realized_closed = pos.quantity == 0

                    if realized_closed:
                        # Position fully closed -> store a trade record
                        trade_record = {
                            "symbol": pos.symbol,
                            "side": pos.side,
                            "closed_qty": close_qty,
                            "avg_entry_price": pos.avg_price,
                            "exit_price": price,
                            "realized_pnl": pos.realized_pnl,
                            "fees": pos.fees + fees,
                            "meta": dict(pos.meta),
                            "closed_at": time.time(),
                        }
                        self._closed_trades.append(trade_record)
                        self._positions.pop(symbol, None)
                    else:
                        # Partial close, still holding some position
                        pos.last_update_ts = time.time()
                        pos.fees += fees

                    # Remaining quantity opens new position in opposite direction
                    if remaining_qty > 0:
                        new_side = "LONG" if side_u == "BUY" else "SHORT"
                        new_pos = Position(
                            symbol=symbol,
                            side=new_side,
                            quantity=remaining_qty,
                            avg_price=price,
                            meta=dict(meta),
                        )
                        self._positions[symbol] = new_pos
                        pos = new_pos
                        realized_closed = False
                else:
                    # Same direction: average in
                    total_qty = pos.quantity + qty
                    if total_qty <= 0:
                        pos.quantity = 0
                        pos.avg_price = price
                        total_qty = qty

                    new_avg = (
                        pos.avg_price * pos.quantity + price * qty
                    ) / float(total_qty)

                    pos.quantity = total_qty
                    pos.avg_price = new_avg
                    pos.last_update_ts = time.time()
                    pos.fees += fees
                    pos.meta.update(meta)

            # Update unrealized PnL for this symbol
            self._update_unrealized_locked(symbol)

            if self._logger:
                try:
                    self._logger.debug(
                        "PositionTracker: applied fill symbol=%s side=%s qty=%s "
                        "price=%.4f realized_pnl=%.4f pos=%s",
                        symbol,
                        side_u,
                        qty,
                        price,
                        realized_pnl,
                        pos.as_dict() if pos else None,
                    )
                except Exception:
                    pass

            return {
                "symbol": symbol,
                "side": pos.side if pos else None,
                "realized_pnl": realized_pnl,
                "position_closed": realized_closed,
            }

    # ------------------------------------------------------------------
    # Fill from ExecutionEngine on_fill event
    # ------------------------------------------------------------------
    def apply_fill_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrates directly with ExecutionEngine.on_fill() style events.

        Expected keys (best-effort, tolerant):
            - symbol
            - side (BUY/SELL)
            - filled_qty or qty
            - avg_fill_price or avg_price or price
            - pnl (optional, used only for logging/consistency)

        Idempotency
        -----------
        If event contains a 'trade_id', the tracker will only apply that
        trade_id once within a short TTL window (default: 6 hours).
        """
        symbol = event.get("symbol")
        side = event.get("side", "BUY")
        qty = event.get("filled_qty") or event.get("qty") or 0
        price = (
            event.get("avg_fill_price")
            or event.get("avg_price")
            or event.get("price")
            or 0.0
        )

        trade_id = event.get("trade_id") or event.get("order_id")
        now = time.time()

        # Simple idempotency guard
        if trade_id:
            with self._lock:
                # clean old ids
                expired_before = now - self._trade_id_ttl_seconds
                to_delete = [
                    tid
                    for tid, ts in self._applied_trade_ids.items()
                    if ts < expired_before
                ]
                for tid in to_delete:
                    self._applied_trade_ids.pop(tid, None)

                if trade_id in self._applied_trade_ids:
                    # Already applied recently -> no-op
                    if self._logger:
                        try:
                            self._logger.debug(
                                "PositionTracker: skipping duplicate trade_id=%s",
                                trade_id,
                            )
                        except Exception:
                            pass
                    return {
                        "symbol": symbol,
                        "side": None,
                        "realized_pnl": 0.0,
                        "position_closed": False,
                    }

                # Mark as applied
                self._applied_trade_ids[trade_id] = now

        meta = {
            "strategy_id": event.get("strategy_id")
            or (event.get("meta") or {}).get("strategy_id"),
            "trade_id": trade_id,
            "close_reason": event.get("close_reason"),
            "raw": dict(event),
        }

        return self.apply_fill(
            symbol=symbol,
            side=side,
            qty=int(qty),
            price=float(price),
            meta=meta,
        )


    # ------------------------------------------------------------------
    # Close position API
    # ------------------------------------------------------------------
    def close_position(
        self,
        symbol: str,
        reason: str = "MANUAL",
        meta: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Force-close an open position at current mark price.

        - Uses price_fetcher(symbol) if available.
        - Otherwise uses the position's avg_price as a best-effort mark.
        """
        symbol = str(symbol)
        meta = meta or {}

        # Snapshot side/qty under lock
        with self._lock:
            pos = self._positions.get(symbol)
            if not pos or pos.quantity <= 0:
                return None
            qty = pos.quantity
            exit_side = "SELL" if pos.side == "LONG" else "BUY"

        # Determine exit price (outside lock)
        price = None
        if self._price_fetcher is not None:
            try:
                price = float(self._price_fetcher(symbol))
            except Exception:
                price = None

        if price is None:
            price = pos.avg_price

        meta = {**meta, "close_reason": reason}

        return self.apply_fill(
            symbol=symbol,
            side=exit_side,
            qty=qty,
            price=price,
            meta=meta,
        )

    # ------------------------------------------------------------------
    # Snapshot / queries
    # ------------------------------------------------------------------
    def get_position(self, symbol: str) -> Optional[Position]:
        with self._lock:
            return self._positions.get(str(symbol))

    def get_all_positions(self) -> Dict[str, Position]:
        with self._lock:
            return dict(self._positions)

    def get_closed_trades(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._closed_trades)

    def get_portfolio_snapshot(
        self,
        equity: Optional[float] = None,
        cash: Optional[float] = None,
    ) -> PortfolioSnapshot:
        """
        Compute a portfolio snapshot.

        - Updates unrealized PnL using price_fetcher where available.
        """
        with self._lock:
            # Refresh unrealized PnL
            for symbol in list(self._positions.keys()):
                self._update_unrealized_locked(symbol)

            total_unrealized = sum(
                p.unrealized_pnl for p in self._positions.values()
            )
            gross_exposure = 0.0
            net_exposure = 0.0
            positions_dict: Dict[str, Dict[str, Any]] = {}

            for symbol, pos in self._positions.items():
                notional = pos.quantity * pos.avg_price
                gross_exposure += abs(notional)
                signed_notional = notional if pos.side == "LONG" else -notional
                net_exposure += signed_notional
                positions_dict[symbol] = pos.as_dict()

            snapshot = PortfolioSnapshot(
                timestamp=time.time(),
                equity=equity,
                cash=cash,
                realized_pnl=self._realized_pnl_total,
                unrealized_pnl=total_unrealized,
                gross_exposure=gross_exposure,
                net_exposure=net_exposure,
                num_open_positions=len(self._positions),
                positions=positions_dict,
            )
            return snapshot

    # ------------------------------------------------------------------
    # Logging helper
    # ------------------------------------------------------------------
    def log_snapshot(
        self,
        equity: Optional[float] = None,
        cash: Optional[float] = None,
    ) -> None:
        """
        Convenience helper to log a portfolio snapshot via the internal logger.

        Message shape:
            {
                "event": "PORTFOLIO_SNAPSHOT",
                ...snapshot.as_dict()
            }
        """
        if not self._logger:
            return

        try:
            snap = self.get_portfolio_snapshot(equity=equity, cash=cash).as_dict()
            payload = {"event": "PORTFOLIO_SNAPSHOT", **snap}
            self._logger.info(payload)
        except Exception:
            # Logging must be best-effort only; never break trading loop.
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _update_unrealized_locked(self, symbol: str) -> None:
        pos = self._positions.get(symbol)
        if not pos:
            return

        mark_price: Optional[float] = None
        if self._price_fetcher is not None:
            try:
                mark_price = float(self._price_fetcher(symbol))
            except Exception:
                mark_price = None

        if mark_price is None:
            mark_price = pos.avg_price

        if pos.side == "LONG":
            pos.unrealized_pnl = (mark_price - pos.avg_price) * pos.quantity
        else:  # SHORT
            pos.unrealized_pnl = (pos.avg_price - mark_price) * pos.quantity

        pos.last_update_ts = time.time()
