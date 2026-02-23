# infra/order_queue.py
"""
OrderQueue: serializes order submissions to the provider, supports throttling, retries,
and optional RiskManager pre-validation (circuit-breaker + symbol-cap).
"""

from typing import Dict, Any
import time


class OrderQueue:
    def __init__(
        self,
        provider,
        throttle_seconds: float = 0.0,
        max_retries: int = 0,
        retry_delay: float = 0.0,
        logger=None,
        risk_manager=None,
    ):
        """
        provider: UnifiedProvider or provider implementing submit_order / submit_order_with_retry
        throttle_seconds: minimum seconds between subsequent order submits.
        max_retries: how many retries to attempt on ERROR responses.
        retry_delay: delay between retries in seconds.
        risk_manager: optional RiskManager instance supporting:
            - is_trading_allowed(account_equity=...)
            - config (dict) with "max_symbol_weight" OR risk_manager.get("max_symbol_weight")
        """
        self.provider = provider
        self.throttle = float(throttle_seconds or 0.0)
        self.max_retries = int(max_retries or 0)
        self.retry_delay = float(retry_delay or 0.0)
        self._last_submit_ts = 0.0
        self._logger = logger
        self.risk = risk_manager

    def _sleep_if_needed(self):
        if self.throttle <= 0:
            return
        now = time.time()
        delta = self.throttle - (now - self._last_submit_ts)
        if delta > 0:
            time.sleep(delta)

    def _circuit_breaker_check(self) -> None:
        """
        Query risk_manager.is_trading_allowed. If it returns False, raise ValueError.
        Uses provider.get_account_nav() as account_equity if available.
        """
        if self.risk is None:
            return
        try:
            if hasattr(self.risk, "is_trading_allowed"):
                acct_eq = None
                try:
                    acct_eq = self.provider.get_account_nav()
                except Exception:
                    acct_eq = None
                try:
                    allowed = self.risk.is_trading_allowed(account_equity=acct_eq)
                except TypeError:
                    # risk impl might not accept kwargs
                    allowed = self.risk.is_trading_allowed()
                except Exception:
                    # on unexpected error, allow trading (fail-safe permissive)
                    allowed = True
                if allowed is False:
                    # tests and existing code expect this exact message in some places
                    raise ValueError("Trading not allowed by circuit breaker")
        except ValueError:
            raise
        except Exception:
            # non-fatal; log and continue
            if self._logger is not None:
                try:
                    self._logger.debug("Circuit-breaker quick check failed (non-fatal)")
                except Exception:
                    pass

    def _symbol_cap_check(self, order: Dict[str, Any]) -> None:
        """
        Perform early symbol-cap enforcement:
        - find max_symbol_weight from risk manager config
        - get provider NAV and positions
        - compute projected exposure for symbol using order quantity and price
        - raise ValueError(f"Symbol cap exceeded for {symbol}") on violation
        """
        if self.risk is None:
            return
        # acquire max_symbol_weight
        max_sym_w = None
        try:
            # try attribute .config first
            cfg = getattr(self.risk, "config", None) or {}
            if isinstance(cfg, dict) and "max_symbol_weight" in cfg:
                max_sym_w = cfg.get("max_symbol_weight")
            else:
                # maybe risk_manager was initialized with config under other attr
                try:
                    max_sym_w = getattr(self.risk, "get", lambda k, d=None: d)(
                        "max_symbol_weight", None
                    )
                except Exception:
                    max_sym_w = None
        except Exception:
            max_sym_w = None

        try:
            max_sym_w_float = float(max_sym_w) if max_sym_w is not None else None
        except Exception:
            max_sym_w_float = None

        # Only proceed if weight configured
        if not max_sym_w_float:
            return

        # Only apply to buy-side orders (or unspecified)
        side = (order.get("side") or "").lower() if isinstance(order, dict) else ""
        if side not in ("", "buy"):
            return

        symbol = order.get("symbol")
        if not symbol:
            return

        # determine NAV
        try:
            nav = None
            try:
                nav = self.provider.get_account_nav()
            except Exception:
                nav = None
            if nav is None:
                return  # cannot enforce without NAV
            nav_val = float(nav)
        except Exception:
            return

        # determine current positions and last price
        try:
            pos_map = {}
            try:
                pos_map = self.provider.get_positions() or {}
            except Exception:
                pos_map = {}
            curr_qty = float(pos_map.get(symbol, 0) or 0)
            # last price heuristics
            last_price = None
            last_key = f"__last_price__:{symbol}"
            if last_key in pos_map:
                try:
                    last_price = float(
                        pos_map.get(last_key) or order.get("price") or 0.0
                    )
                except Exception:
                    last_price = float(order.get("price") or 0.0)
            else:
                # provider may expose a _last_prices dict or similar; try getattr
                try:
                    last_price = float(
                        getattr(self.provider, "_last_prices", {}).get(
                            symbol, order.get("price") or 0.0
                        )
                    )
                except Exception:
                    last_price = float(order.get("price") or 0.0)
            # order qty and price
            try:
                qty = float(order.get("quantity") or order.get("qty") or 0)
            except Exception:
                qty = 0.0
            price = float(order.get("price") or last_price or 0.0)
            projected_qty = curr_qty + qty
            projected_value = projected_qty * price
            if projected_value > (nav_val * max_sym_w_float):
                raise ValueError(f"Symbol cap exceeded for {symbol}")
        except ValueError:
            raise
        except Exception:
            if self._logger is not None:
                try:
                    self._logger.debug("Early symbol-cap check failed (non-fatal)")
                except Exception:
                    pass

    def submit(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an order through the provider, respecting throttle, retries, and risk checks.
        May raise ValueError for risk rejections.
        """
        # run pre-checks
        self._circuit_breaker_check()
        self._symbol_cap_check(order)

        # throttle
        self._sleep_if_needed()

        # submit via provider (with provider-level retries if available)
        if hasattr(self.provider, "submit_order_with_retry"):
            try:
                resp = self.provider.submit_order_with_retry(
                    order,
                    retries=self.max_retries,
                    retry_delay=self.retry_delay,
                    raise_on_risk=True,
                )
            except TypeError:
                # provider doesn't support raise_on_risk
                resp = self.provider.submit_order_with_retry(
                    order, retries=self.max_retries, retry_delay=self.retry_delay
                )
            except ValueError:
                # bubble up risk errors
                raise
        else:
            # try direct submit with retries loop here
            last = None
            for attempt in range(self.max_retries + 1):
                try:
                    if hasattr(self.provider, "submit_order"):
                        last = self.provider.submit_order(order)
                    elif hasattr(self.provider, "submit"):
                        last = self.provider.submit(order)
                    else:
                        last = {"status": "ERROR", "reason": "NO_SUBMIT_METHOD"}
                except Exception as e:
                    last = {
                        "status": "ERROR",
                        "reason": "EXCEPTION",
                        "exception": str(e),
                    }
                if last and last.get("status") not in ("ERROR",):
                    resp = last
                    break
                if attempt < self.max_retries and self.retry_delay > 0:
                    time.sleep(self.retry_delay)
            else:
                resp = last
        self._last_submit_ts = time.time()
        return resp
