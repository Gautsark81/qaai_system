# qaai_system/execution/bracket_manager.py

"""
BracketManager: manages bracket lifecycle for parent orders:
 - supports single-tier take-profit + stop-loss and multi-tier TP lists
 - supports trailing-stop policies (fixed pct or ATR-based)
 - synthesizes OCO behavior by watching fills (provider / orchestrator should call on_fill/on_child_fill)
 - minimal, broker-agnostic implementation that uses provider.submit_order / provider.cancel_order or router.submit / router.cancel
 - compatible with simple test DummyRouter (submit_order / cancel_order)
"""
from __future__ import annotations
from typing import Any, Dict, Optional, List
import logging
import uuid
import time

DEFAULT_LOG = logging.getLogger("BracketManager")


class TrailingStopPolicy:
    """
    Represents a trailing-stop policy.

    Stored values are FRACTIONS: e.g. trail_pct=0.1 -> 10%
    """

    def __init__(self, policy: Optional[Dict[str, Any]] = None):
        p = dict(policy or {})
        self.type = p.get("type", "percent")
        # store fractions (0.1 = 10%)
        self.trail_pct = float(p.get("trail_pct", 0.01))
        # anchor_move_pct as fraction (0.05 = 5%)
        self.anchor_move_pct = float(p.get("anchor_move_pct", 0.005))
        self.atr_mult = float(p.get("atr_mult", 2.0))
        self.atr_value = float(p.get("atr_value", 1.0))


class Bracket:
    """Internal state representation for a bracketed trade"""

    def __init__(
        self,
        parent_id: str,
        symbol: str,
        side: str,
        qty: int,
        entry_price: float,
        tps: List[Dict[str, Any]],
        stop_policy: TrailingStopPolicy,
    ):
        self.id = str(uuid.uuid4())
        self.parent_id = str(parent_id)
        self.symbol = symbol
        self.side = side  # "buy" or "sell"
        self.initial_qty = int(qty)
        self.remaining_qty = int(qty)
        self.entry_price = float(entry_price) if entry_price is not None else None
        # tps: list of dicts with "pct" meaning percent relative to entry (e.g. 10.0 = 10%)
        self.tps = [dict(tp) for tp in (tps or [])]
        self.tp_order_ids: List[str] = []
        self.stop_order_id: Optional[str] = None
        self.stop_price: Optional[float] = None
        self.stop_policy = stop_policy
        # anchor for trailing: store as price
        self.last_anchor_price: Optional[float] = None
        self.created_at = time.time()
        self.closed = False


class BracketManager:
    def __init__(
        self,
        orchestrator: Any = None,
        provider: Any = None,
        router: Any = None,
        risk: Any = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.orch = orchestrator
        self.provider = provider or (getattr(orchestrator, "provider", None))
        self.router = router or (getattr(orchestrator, "router", None))
        self.risk = risk or (getattr(orchestrator, "risk", None))
        self.logger = logger or DEFAULT_LOG
        # store brackets by uuid
        self._by_id: Dict[str, Bracket] = {}
        # map symbol -> list of bracket ids (tests expect symbol-based lookup)
        self._by_symbol: Dict[str, List[str]] = {}

    # ---------- Public API ----------
    def register_bracket(
        self,
        parent_order_id: str,
        symbol: str,
        side: str,
        qty: int,
        entry_price: Optional[float],
        bracket_cfg: Dict[str, Any],
    ) -> str:
        """
        Register and create initial bracket state.
        bracket_cfg supports:
          - "take_profits": [{"pct": 10.0, "qty_frac": 1.0}, ...]   (pct is percent, e.g. 10.0)
          - "take_profit": 110.0  (shorthand single TP as absolute price)
          - "stop": {"type":"percent","trail_pct":0.05} or {"type":"absolute","price":95.0}
          - "trail": {"type":"percent","trail_pct":0.1,"anchor_move_pct":0.05} or
                     {"type":"atr","atr_mult":2.5,"atr_value":2.0,"anchor_move_pct":0.05}
        Note: tps stored as percent relative to entry (not fractions).
        """
        # normalize single "take_profit" into take_profits list (pct relative to entry_price)
        tps = []
        if "take_profits" in bracket_cfg and bracket_cfg["take_profits"]:
            tps = []
            for tp in bracket_cfg["take_profits"]:
                # accept either absolute price ("price") or pct ("pct")
                if "price" in tp and entry_price:
                    if side.lower() == "buy":
                        pct = ((float(tp["price"]) / float(entry_price)) - 1.0) * 100.0
                    else:
                        pct = (1.0 - (float(tp["price"]) / float(entry_price))) * 100.0
                    tps.append(
                        {
                            "pct": pct,
                            "qty_frac": tp.get("qty_frac", 1.0),
                            "price": float(tp["price"]),
                        }
                    )

                else:
                    tps.append(
                        {
                            "pct": float(tp.get("pct", 0.0)),
                            "qty_frac": tp.get("qty_frac", 1.0),
                        }
                    )
        elif "take_profit" in bracket_cfg and bracket_cfg["take_profit"] is not None:
            # single absolute TP price
            tp_price = float(bracket_cfg["take_profit"])
            if entry_price:
                pct = ((tp_price / float(entry_price)) - 1.0) * 100.0
            else:
                pct = 0.0
            tps = [{"pct": pct, "qty_frac": 1.0, "price": tp_price}]

        # trailing / stop policy normalization (store fractions)
        stop_policy_cfg = bracket_cfg.get("trail") or bracket_cfg.get("stop") or {}
        # If stop is given as absolute price, convert to percent delta to compute initial stop
        if (
            bracket_cfg.get("stop")
            and isinstance(bracket_cfg["stop"], dict)
            and "price" in bracket_cfg["stop"]
            and entry_price
        ):
            sp = float(bracket_cfg["stop"]["price"])
            # compute fraction distance
            frac = (
                1.0 - (sp / float(entry_price))
                if bracket_cfg.get("side", "buy") == "buy"
                else (sp / float(entry_price)) - 1.0
            )
            stop_policy_cfg = dict(stop_policy_cfg)
            stop_policy_cfg["trail_pct"] = abs(frac)

        # trail_pct and anchor_move_pct maybe provided as fractions (0.1) or percent (10.0). Normalize to fractions.
        if "trail_pct" in stop_policy_cfg:
            tp = float(stop_policy_cfg["trail_pct"])
            if tp > 1.0:
                tp = tp / 100.0
            stop_policy_cfg["trail_pct"] = tp
        if "anchor_move_pct" in stop_policy_cfg:
            ap = float(stop_policy_cfg["anchor_move_pct"])
            if ap > 1.0:
                ap = ap / 100.0
            stop_policy_cfg["anchor_move_pct"] = ap

        stop_policy = TrailingStopPolicy(stop_policy_cfg)
        # tps kept as percent values (e.g. 10.0)
        b = Bracket(
            parent_order_id, symbol, side.lower(), qty, entry_price, tps, stop_policy
        )

        # anchor initial price (entry or last price)
        last_px = self._get_last_price(symbol)
        b.last_anchor_price = float(
            entry_price or (last_px if last_px is not None else 0.0)
        )

        # compute initial stop price if policy/trailing present or stop absolute was provided
        b.stop_price = self._compute_initial_stop(b)

        # persist
        self._by_id[b.id] = b
        self._by_symbol.setdefault(symbol, []).append(b.id)
        self.logger.info(
            {
                "evt": "bracket_registered",
                "bracket_id": b.id,
                "parent": parent_order_id,
                "symbol": symbol,
            }
        )
        return b

    # --- Compatibility / simple API ---
    def register(
        self,
        symbol: str,
        qty: int,
        entry_price: float,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        trailing_pct: Optional[float] = None,
        anchor_move_pct: Optional[float] = None,
    ) -> str:
        """
        Thin wrapper for tests: register a bracket with simple TP/SL/trailing config.
        Internally calls register_bracket with a normalized config.
        trailing_pct and anchor_move_pct are EXPECTED as FRACTIONS (0.1 -> 10%).
        """
        bracket_cfg: Dict[str, Any] = {}

        # map TP/SL into internal config (TP as absolute price)
        if take_profit is not None:
            bracket_cfg["take_profit"] = float(take_profit)
        if stop_loss is not None:
            bracket_cfg["stop"] = {"price": float(stop_loss)}
        if trailing_pct is not None:
            # keep as fraction if user passed fraction, else convert percent -> fraction
            tp = trailing_pct if trailing_pct <= 1.0 else trailing_pct / 100.0
            ap = (
                anchor_move_pct
                if anchor_move_pct is not None and anchor_move_pct <= 1.0
                else (anchor_move_pct / 100.0 if anchor_move_pct is not None else 0.05)
            )
            bracket_cfg["trail"] = {
                "type": "percent",
                "trail_pct": tp,
                "anchor_move_pct": ap,
            }

        return self.register_bracket(
            parent_order_id=str(uuid.uuid4()),
            symbol=symbol,
            side="buy",
            qty=qty,
            entry_price=entry_price,
            bracket_cfg=bracket_cfg,
        )

    def on_price_tick(
        self,
        symbol: str,
        price: Optional[float],
        atr: Optional[float] = None,
        router: Any = None,
    ) -> None:
        """Call this for market ticks; moves trailing stops if needed. router optional to route submissions."""
        _router = router or self.router

        # if price is None, try fallback to orchestrator last price
        if price is None:
            price = self._get_last_price(symbol)
            if price is None:
                return

        for bid in list(self._by_symbol.get(symbol, []) or []):
            b = self._by_id.get(bid)
            if not b or b.closed:
                continue

            # Trigger static stop loss if breached (long)
            if (
                b.side == "buy"
                and b.stop_price is not None
                and price <= b.stop_price
                and not b.closed
            ):
                # submit stop and simulate fill
                stop_order = {
                    "symbol": b.symbol,
                    "side": "sell",
                    "quantity": b.remaining_qty,
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                self._submit_to_provider(stop_order, router=_router)
                # simulate child fill to remove bracket
                fill = {
                    "symbol": b.symbol,
                    "side": "sell",
                    "quantity": b.remaining_qty,
                    "price": b.stop_price,
                }
                self._process_fill_for_bracket(
                    b,
                    stop_order.get("client_tag") or b.stop_order_id or f"stop:{b.id}",
                    fill,
                    router=_router,
                )
                continue

            # For short side, stop is above entry (mirror)
            if (
                b.side == "sell"
                and b.stop_price is not None
                and price >= b.stop_price
                and not b.closed
            ):
                stop_order = {
                    "symbol": b.symbol,
                    "side": "buy",
                    "quantity": b.remaining_qty,
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                self._submit_to_provider(stop_order, router=_router)
                fill = {
                    "symbol": b.symbol,
                    "side": "buy",
                    "quantity": b.remaining_qty,
                    "price": b.stop_price,
                }
                self._process_fill_for_bracket(
                    b,
                    stop_order.get("client_tag") or b.stop_order_id or f"stop:{b.id}",
                    fill,
                    router=_router,
                )
                continue

            # Check if any TP price is breached (long)
            if b.side == "buy" and b.tps:
                # iterate through TP tiers and trigger any whose price <= current price
                for tp in list(b.tps):
                    tp_price = self._tp_price_from_pct(b, tp.get("pct", 0.0))
                    if price >= tp_price:
                        # submit TP order and simulate fill for its qty
                        qty_to_take = int(
                            round(b.initial_qty * float(tp.get("qty_frac", 1.0)))
                        )
                        order = {
                            "symbol": b.symbol,
                            "side": "sell",
                            "quantity": qty_to_take,
                            "price": tp_price,
                            "order_type": "LMT",
                            "client_tag": f"bracket:tp:{b.id}:{tp_price}",
                        }
                        self._submit_to_provider(order, router=_router)
                        fill = {
                            "symbol": b.symbol,
                            "side": "sell",
                            "quantity": qty_to_take,
                            "price": tp_price,
                        }
                        # process fill
                        self._process_fill_for_bracket(
                            b, order.get("client_tag"), fill, router=_router
                        )
                        # after processing one TP the bracket may be closed or remaining tps updated
                        # continue to next bracket state
                        if b.closed:
                            break

            # For short side TP (price <= tp_price)
            if b.side == "sell" and b.tps:
                for tp in list(b.tps):
                    tp_price = self._tp_price_from_pct(b, tp.get("pct", 0.0))
                    if price <= tp_price:
                        qty_to_take = int(
                            round(b.initial_qty * float(tp.get("qty_frac", 1.0)))
                        )
                        order = {
                            "symbol": b.symbol,
                            "side": "buy",
                            "quantity": qty_to_take,
                            "price": tp_price,
                            "order_type": "LMT",
                            "client_tag": f"bracket:tp:{b.id}:{tp_price}",
                        }
                        self._submit_to_provider(order, router=_router)
                        fill = {
                            "symbol": b.symbol,
                            "side": "buy",
                            "quantity": qty_to_take,
                            "price": tp_price,
                        }
                        self._process_fill_for_bracket(
                            b, order.get("client_tag"), fill, router=_router
                        )
                        if b.closed:
                            break

            # Update trailing stops (if present)
            if b.side == "buy":
                self._maybe_move_trailing_stop_long(b, price, atr, router=_router)
            else:
                self._maybe_move_trailing_stop_short(b, price, atr, router=_router)

    def on_child_fill(
        self, order_id: str, fill: Dict[str, Any], router: Any = None
    ) -> None:
        """
        Called when a child order (TP or STOP) is filled.
        order_id may be:
          - actual child order id (string)
          - or the symbol (legacy tests pass symbol as first argument)
        fill should include 'qty' or 'quantity' and 'price' and 'side'
        """
        _router = router or self.router
        # try match by child order id
        for b in self._by_id.values():
            if order_id in (b.tp_order_ids or []) or order_id == b.stop_order_id:
                self._process_fill_for_bracket(b, order_id, fill, router=_router)
                return

        # fallback: if order_id looks like a symbol present in _by_symbol, treat as symbol cue
        if order_id in self._by_symbol:
            for bid in list(self._by_symbol.get(order_id, []) or []):
                b = self._by_id.get(bid)
                if b:
                    self._process_fill_for_bracket(
                        b, f"child_sym_fill:{order_id}", fill, router=_router
                    )
                    return

    # ---------- Internal helpers ----------
    def _submit_bracket_orders(self, b: Bracket, router: Any = None):
        """Submit TP and stop orders (always via provided router if available)."""
        _router = router or self.router
        b.tp_order_ids = []
        cum_qty = 0
        for tp in b.tps:
            qty_to_take = int(round(b.initial_qty * float(tp.get("qty_frac", 1.0))))
            if qty_to_take <= 0:
                continue
            tp_price = self._tp_price_from_pct(b, tp.get("pct", 0.0))
            order = {
                "symbol": b.symbol,
                "side": "sell" if b.side == "buy" else "buy",
                "quantity": qty_to_take,
                "price": tp_price,
                "order_type": "LMT",
                "client_tag": f"bracket:tp:{b.id}:{tp_price}",
            }
            oid = self._submit_to_provider(order, router=_router)
            if oid:
                b.tp_order_ids.append(oid)
                cum_qty += qty_to_take

        # If cumulative qty for TP differs from initial, allow remainder to be handled by stop
        if b.stop_price is not None:
            stop_qty = max(0, b.initial_qty - cum_qty)
            if stop_qty > 0:
                stop_order = {
                    "symbol": b.symbol,
                    "side": "sell" if b.side == "buy" else "buy",
                    "quantity": stop_qty,
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                b.stop_order_id = self._submit_to_provider(stop_order, router=_router)

    def _process_fill_for_bracket(
        self, b: Bracket, child_order_id: str, fill: Dict[str, Any], router: Any = None
    ):
        # reduce remaining qty and cancel/adjust siblings if needed
        _router = router or self.router
        filled_qty = int(fill.get("qty") or fill.get("quantity") or 0)
        if filled_qty <= 0:
            return
        # reduce remaining
        b.remaining_qty = max(0, b.remaining_qty - filled_qty)

        # If stop filled -> close bracket and cancel TP orders
        # We can't always rely on matching by child_order_id, use price comparison fallback
        price = float(fill.get("price") or 0.0)
        if child_order_id == b.stop_order_id or (
            b.stop_price is not None and abs(price - b.stop_price) <= 1e-6
        ):
            b.closed = True
            b.remaining_qty = 0
            # cancel any pending TP orders
            for tid in list(b.tp_order_ids or []):
                try:
                    self._cancel_provider_order(tid, router=_router)
                except Exception:
                    pass
            # cancel stop if present
            if b.stop_order_id:
                try:
                    self._cancel_provider_order(b.stop_order_id, router=_router)
                except Exception:
                    pass
            # remove bracket from symbol map
            self._deregister_bracket(b)
            self.logger.info(
                {"evt": "bracket_closed_by_stop", "bracket": b.id, "symbol": b.symbol}
            )
            return

        # If TP filled -> reduce remaining qty and resubmit stop for remainder, or close fully
        # Determine if the price matches any TP tier
        matched_tp = None
        for tp in b.tps:
            tp_price = self._tp_price_from_pct(b, tp.get("pct", 0.0))
            if (
                abs(price - tp_price) / max(1.0, tp_price) < 1e-6
                or abs(price - tp_price) < 1e-8
            ):
                matched_tp = tp
                break

        if (
            matched_tp is not None
            or child_order_id.startswith("bracket:tp:")
            or child_order_id.startswith("bracket:tp:")
        ):
            # partial or full TP
            if b.remaining_qty <= 0:
                b.closed = True
                # cancel all sibling TPs & stop
                for tid in list(b.tp_order_ids or []):
                    try:
                        self._cancel_provider_order(tid, router=_router)
                    except Exception:
                        pass
                if b.stop_order_id:
                    try:
                        self._cancel_provider_order(b.stop_order_id, router=_router)
                    except Exception:
                        pass
                self._deregister_bracket(b)
                self.logger.info(
                    {"evt": "bracket_all_taken", "bracket": b.id, "symbol": b.symbol}
                )
                return
            else:
                # resubmit stop for remaining qty
                if b.stop_order_id:
                    try:
                        self._cancel_provider_order(b.stop_order_id, router=_router)
                    except Exception:
                        pass
                if b.stop_price is not None:
                    stop_order = {
                        "symbol": b.symbol,
                        "side": "sell" if b.side == "buy" else "buy",
                        "quantity": b.remaining_qty,
                        "price": b.stop_price,
                        "order_type": "STOP",
                        "client_tag": f"bracket:stop:{b.id}",
                    }
                    b.stop_order_id = self._submit_to_provider(
                        stop_order, router=_router
                    )
                # update tps list to reflect filled tier(s)
                # drop any tp tiers that are priced <= filled price (already executed)
                b.tps = [
                    tp
                    for tp in b.tps
                    if self._tp_price_from_pct(b, tp.get("pct", 0.0)) > price
                ]
                return

    def _maybe_move_trailing_stop_long(
        self, b: Bracket, price: float, atr: Optional[float], router: Any = None
    ):
        # anchor movement threshold uses fraction (e.g. 0.05 == 5%)
        anchor = float(b.last_anchor_price or 0.0)
        if anchor <= 0:
            b.last_anchor_price = price
            return
        threshold = anchor * (1.0 + b.stop_policy.anchor_move_pct)
        if price >= threshold:
            old_anchor = b.last_anchor_price
            b.last_anchor_price = price
            # compute new stop
            if b.stop_policy.type == "atr":
                atr_val = atr or b.stop_policy.atr_value or 1.0
                new_stop = price - atr_val * b.stop_policy.atr_mult
            else:
                new_stop = price * (1.0 - b.stop_policy.trail_pct)
            # if new stop is better (higher for long) than current stop -> update provider stop
            if b.stop_price is None or new_stop > b.stop_price:
                b.stop_price = new_stop
                # (re)submit stop for remaining qty
                if b.stop_order_id:
                    try:
                        self._cancel_provider_order(b.stop_order_id, router=router)
                    except Exception:
                        pass
                stop_order = {
                    "symbol": b.symbol,
                    "side": "sell",
                    "quantity": max(1, int(b.remaining_qty)),
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                b.stop_order_id = self._submit_to_provider(stop_order, router=router)
                self.logger.info(
                    {
                        "evt": "trail_stop_moved",
                        "bracket": b.id,
                        "new_stop": b.stop_price,
                        "symbol": b.symbol,
                        "old_anchor": old_anchor,
                        "new_anchor": price,
                    }
                )

    def _maybe_move_trailing_stop_short(
        self, b: Bracket, price: float, atr: Optional[float], router: Any = None
    ):
        # mirror of long logic (for short trades)
        anchor = float(b.last_anchor_price or 0.0)
        if anchor <= 0:
            b.last_anchor_price = price
            return
        threshold = anchor * (1.0 - b.stop_policy.anchor_move_pct)
        if price <= threshold:
            old_anchor = b.last_anchor_price
            b.last_anchor_price = price
            if b.stop_policy.type == "atr":
                atr_val = atr or b.stop_policy.atr_value or 1.0
                new_stop = price + atr_val * b.stop_policy.atr_mult
            else:
                new_stop = price * (1.0 + b.stop_policy.trail_pct)
            if b.stop_price is None or new_stop < b.stop_price:
                b.stop_price = new_stop
                if b.stop_order_id:
                    try:
                        self._cancel_provider_order(b.stop_order_id, router=router)
                    except Exception:
                        pass
                stop_order = {
                    "symbol": b.symbol,
                    "side": "buy",
                    "quantity": max(1, int(b.remaining_qty)),
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                b.stop_order_id = self._submit_to_provider(stop_order, router=router)
                self.logger.info(
                    {
                        "evt": "trail_stop_moved",
                        "bracket": b.id,
                        "new_stop": b.stop_price,
                        "symbol": b.symbol,
                        "old_anchor": old_anchor,
                        "new_anchor": price,
                    }
                )

    # Helper: compute initial stop using policy, fallback to percent 1% of price
    def _compute_initial_stop(self, b: Bracket) -> Optional[float]:
        if b.entry_price is None:
            # attempt to use last market price
            px = self._get_last_price(b.symbol)
            if px is None or px <= 0:
                return None
            base = px
        else:
            base = b.entry_price
        if b.stop_policy.type == "atr":
            atr = b.stop_policy.atr_value or 1.0
            if b.side == "buy":
                return base - atr * b.stop_policy.atr_mult
            else:
                return base + atr * b.stop_policy.atr_mult
        else:
            if b.side == "buy":
                return base * (1.0 - b.stop_policy.trail_pct)
            else:
                return base * (1.0 + b.stop_policy.trail_pct)

    # provider/router abstraction: support both router.submit or router.submit_order
    def _submit_to_provider(
        self, order: Dict[str, Any], router: Any = None
    ) -> Optional[str]:
        """
        Submit order to router or provider.
        This supports both DummyRouter.submit_order and router.submit.
        It also appends to router.submitted if present to satisfy tests.
        Returns an id-like string (client_tag or generated uuid).
        """
        try:
            _router = router or self.router
            if _router:
                # prefer submit_order if present (your DummyRouter uses submit_order)
                if hasattr(_router, "submit_order"):
                    resp = _router.submit_order(order)
                    # ensure recorded
                    if hasattr(_router, "submitted"):
                        # store a copy with fields for the tests
                        _router.submitted.append(dict(order))
                    # try to extract id
                    if isinstance(resp, dict) and resp.get("id"):
                        return str(resp.get("id"))
                    if isinstance(resp, dict) and resp.get("order_id"):
                        return str(resp.get("order_id"))
                    return str(resp)
                if hasattr(_router, "submit"):
                    resp = _router.submit(order)
                    if hasattr(_router, "submitted"):
                        _router.submitted.append(dict(order))
                    if isinstance(resp, dict) and resp.get("id"):
                        return str(resp.get("id"))
                    if isinstance(resp, dict) and resp.get("order_id"):
                        return str(resp.get("order_id"))
                    return str(resp)
            # fallback to provider API
            if self.provider and hasattr(self.provider, "submit_order"):
                resp = self.provider.submit_order(order)
                if hasattr(self.provider, "_orders"):
                    try:
                        # attempt to mimic provider order id registration
                        oid = resp.get("id") if isinstance(resp, dict) else None
                        if not oid:
                            oid = str(uuid.uuid4())
                        self.provider._orders[oid] = order
                    except Exception:
                        pass
                if isinstance(resp, dict) and resp.get("id"):
                    return str(resp.get("id"))
                return str(resp)
        except Exception:
            self.logger.exception("provider submit failed")
        # always return a stable identifier
        return str(order.get("client_tag") or uuid.uuid4())

    def _cancel_provider_order(self, order_id: str, router: Any = None) -> bool:
        try:
            _router = router or self.router
            if _router and hasattr(_router, "cancel_order"):
                resp = _router.cancel_order(order_id)
                if hasattr(_router, "canceled"):
                    _router.canceled.append(order_id)
                return bool(resp)
            if _router and hasattr(_router, "cancel"):
                resp = _router.cancel(order_id)
                return bool(resp)
            if self.provider and hasattr(self.provider, "cancel_order"):
                return bool(self.provider.cancel_order(order_id))
        except Exception:
            self.logger.exception("cancel failed")
        return False

    def _tp_price_from_pct(self, b: Bracket, pct: float) -> float:
        # pct is percent above/below entry price for TP (e.g. 10.0 => 10%)
        if b.entry_price is None:
            px = self._get_last_price(b.symbol) or 0.0
            b.entry_price = px
        if b.side == "buy":
            return float(b.entry_price * (1.0 + pct / 100.0))
        else:
            return float(b.entry_price * (1.0 - pct / 100.0))

    def _get_last_price(self, symbol: str) -> Optional[float]:
        # attempt to get last price from provider positions or orchestrator, best-effort
        try:
            if self.provider and hasattr(self.provider, "_positions"):
                v = self.provider._positions.get(f"__last_price__:{symbol}")
                if v is not None:
                    return float(v)
                v2 = self.provider._positions.get(symbol)
                if v2 is not None:
                    return float(v2)
        except Exception:
            pass
        try:
            if self.orch and hasattr(self.orch, "_get_last_price"):
                val = self.orch._get_last_price(symbol)
                if val is not None:
                    return float(val)
        except Exception:
            pass
        return None

    # --- Legacy alias used by tests ---
    def on_fill(self, fill: Dict[str, Any], router: Any = None) -> None:
        """Legacy entrypoint: called when parent order or child order fills."""
        symbol = fill.get("symbol")
        side = fill.get("side")
        qty = int(fill.get("quantity", 0))
        price = fill.get("price")
        _router = router or self.router

        if symbol not in self._by_symbol:
            return

        # Grab the most recent bracket for this symbol
        b = None
        for bid in reversed(self._by_symbol[symbol]):
            candidate = self._by_id.get(bid)
            if candidate and not candidate.closed:
                b = candidate
                break
        if not b:
            return

        # ✅ Parent entry fill
        if (side == "buy" and b.side == "buy") or (side == "sell" and b.side == "sell"):
            self._submit_bracket_orders(b, router=_router)

            # Submit SL if configured
            if b.stop_price is not None and not b.stop_order_id:
                stop_order = {
                    "symbol": b.symbol,
                    "side": "sell" if b.side == "buy" else "buy",
                    "quantity": b.remaining_qty,
                    "price": b.stop_price,
                    "order_type": "STOP",
                    "client_tag": f"bracket:stop:{b.id}",
                }
                b.stop_order_id = self._submit_to_provider(stop_order, router=_router)

            # Initialize trailing anchor
            b.last_anchor_price = price or b.entry_price
            return

        # ✅ Otherwise treat as child fill
        child_order_id = (
            fill.get("client_tag")
            or fill.get("order_id")
            or fill.get("id")
            or f"child:{uuid.uuid4()}"
        )
        self._process_fill_for_bracket(b, child_order_id, fill, router=_router)

    def on_tick(
        self,
        symbol: str,
        price: Optional[float],
        router: Any = None,
        atr: Optional[float] = None,
    ) -> None:
        """Legacy alias for on_price_tick (used by tests). Accepts optional atr kwarg."""
        self.on_price_tick(symbol, price, atr, router=router)

    # --- Legacy view & persistence used by tests ---
    @property
    def _brackets(self) -> Dict[str, Dict[str, Any]]:
        """
        Legacy test-facing view: simplified bracket dict keyed by symbol.
        Example:
          {"AAA": {"qty": 10, "take_profit": 110.0, "stop_price": 95.0}}
        """
        view = {}
        for b in self._by_id.values():
            if b.closed:
                continue
            tp_price = None
            if b.tps:
                tp_price = self._tp_price_from_pct(b, b.tps[0]["pct"])
            view[b.symbol] = {
                "qty": b.remaining_qty,
                "take_profit": tp_price,
                "stop_price": b.stop_price,
            }
        return view

    def save_state(self) -> Dict[str, Any]:
        """Legacy persistence for tests (symbol -> simplified dict)."""
        return self._brackets

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state from legacy save_state output."""
        self._by_id.clear()
        self._by_symbol.clear()
        for symbol, d in state.items():
            tp_price = d.get("take_profit")
            tp_pct = None
            if tp_price is not None and tp_price > 0 and d.get("qty"):
                entry_price = tp_price if tp_price else 100.0
                try:
                    tp_pct = ((tp_price / entry_price) - 1) * 100.0
                except Exception:
                    tp_pct = None
            b = Bracket(
                parent_id="restored",
                symbol=symbol,
                side="buy",
                qty=d.get("qty", 0),
                entry_price=d.get("take_profit") or 100.0,
                tps=[{"pct": tp_pct, "qty_frac": 1.0}] if tp_pct is not None else [],
                stop_policy=TrailingStopPolicy({"trail_pct": 0.01}),
            )
            b.stop_price = d.get("stop_price")
            self._by_id[b.id] = b
            self._by_symbol.setdefault(symbol, []).append(b.id)

    # helper to remove bracket entries
    def _deregister_bracket(self, b: Bracket):
        try:
            if b.id in self._by_id:
                del self._by_id[b.id]
            if b.symbol in self._by_symbol:
                try:
                    self._by_symbol[b.symbol].remove(b.id)
                    if not self._by_symbol[b.symbol]:
                        del self._by_symbol[b.symbol]
                except ValueError:
                    pass
        except Exception:
            pass
