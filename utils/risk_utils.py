# utils/risk_utils.py
from typing import Any, Dict, Optional


def _get_nav_from_provider(provider) -> Optional[float]:
    try:
        if hasattr(provider, "get_account_nav"):
            return provider.get_account_nav()
        return float(getattr(provider, "_account_nav", None) or 0.0)
    except Exception:
        return None


def _get_positions_from_provider(provider) -> Dict[str, Any]:
    try:
        if hasattr(provider, "get_positions"):
            return provider.get_positions() or {}
        return dict(getattr(provider, "_positions", {}) or {})
    except Exception:
        return {}


def enforce_risk_or_raise(risk_manager, provider, order: Dict[str, Any]) -> None:
    if risk_manager is None:
        return

    # Circuit-breaker
    try:
        if hasattr(risk_manager, "is_trading_allowed"):
            acct_eq = _get_nav_from_provider(provider)
            try:
                allowed = risk_manager.is_trading_allowed(account_equity=acct_eq)
            except TypeError:
                allowed = risk_manager.is_trading_allowed()
            except Exception:
                allowed = True
            if allowed is False:
                raise ValueError("Trading not allowed by circuit breaker")
    except ValueError:
        raise
    except Exception:
        return

    # Symbol-cap (early) check
    try:
        cfg = getattr(risk_manager, "config", {}) or {}
        max_sym_w = cfg.get("max_symbol_weight", None)
        try:
            max_sym_w = float(max_sym_w) if max_sym_w is not None else None
        except Exception:
            max_sym_w = None
        if not max_sym_w:
            return

        side = (order.get("side") or "").lower()
        if side not in ("", "buy"):
            return

        symbol = order.get("symbol")
        if not symbol:
            return

        nav_val = _get_nav_from_provider(provider)
        if nav_val is None:
            return

        pos_map = _get_positions_from_provider(provider)
        curr_qty = float(pos_map.get(symbol, 0) or 0)

        last_price_key = f"__last_price__:{symbol}"
        if last_price_key in pos_map:
            last_price = float(pos_map.get(last_price_key) or order.get("price") or 0.0)
        else:
            last_price = float(
                getattr(provider, "_last_prices", {}).get(
                    symbol, order.get("price") or 0.0
                )
            )

        qty = float(order.get("quantity") or order.get("qty") or 0)
        price = float(order.get("price") or last_price or 0.0)
        projected_value = (curr_qty + qty) * price
        if projected_value > (float(nav_val) * float(max_sym_w)):
            raise ValueError(f"Symbol cap exceeded for {symbol}")
    except ValueError:
        raise
    except Exception:
        return
