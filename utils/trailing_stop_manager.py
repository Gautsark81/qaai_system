# File: utils/trailing_stop_manager.py

import logging


class TrailingStopManager:
    def __init__(self, order_id, side, entry_price, config, atr=None):
        self.order_id = order_id
        self.side = side
        self.entry_price = entry_price
        self.config = config
        self.atr = atr or 1.0
        self.triggered = False
        self.logger = logging.getLogger("TrailingStopManager")

        self.trail_type = config.get("trailing_type", "volatility_adaptive")
        self.sl_price = self._initial_stop()

    def _initial_stop(self):
        base_pct = self.config.get("stop_loss_pct", 0.02)
        if self.trail_type == "volatility_adaptive":
            return self._calc_volatility_sl()
        return (
            self.entry_price * (1 - base_pct)
            if self.side == "buy"
            else self.entry_price * (1 + base_pct)
        )

    def _calc_volatility_sl(self):
        atr_mult = self.config.get("atr_multiplier", 1.5)
        trail_amount = self.atr * atr_mult
        return (
            self.entry_price - trail_amount
            if self.side == "buy"
            else self.entry_price + trail_amount
        )

    def update(self, current_price):
        updated = False

        if self.trail_type == "volatility_adaptive":
            if self.side == "buy" and current_price > self.entry_price:
                new_sl = current_price - self.atr * self.config.get(
                    "atr_multiplier", 1.5
                )
                if new_sl > self.sl_price:
                    self.sl_price = new_sl
                    updated = True

            elif self.side == "sell" and current_price < self.entry_price:
                new_sl = current_price + self.atr * self.config.get(
                    "atr_multiplier", 1.5
                )
                if new_sl < self.sl_price:
                    self.sl_price = new_sl
                    updated = True

        elif self.trail_type == "step_triggered":
            trigger_pct = self.config.get("step_trigger_pct", 0.02)
            threshold = self.entry_price * (
                1 + trigger_pct if self.side == "buy" else 1 - trigger_pct
            )
            if (self.side == "buy" and current_price > threshold) or (
                self.side == "sell" and current_price < threshold
            ):
                new_sl = (
                    current_price * (1 - self.config.get("stop_loss_pct", 0.02))
                    if self.side == "buy"
                    else current_price * (1 + self.config.get("stop_loss_pct", 0.02))
                )
                if (self.side == "buy" and new_sl > self.sl_price) or (
                    self.side == "sell" and new_sl < self.sl_price
                ):
                    self.sl_price = new_sl
                    updated = True

        elif self.trail_type == "break_even":
            trigger_pct = self.config.get("break_even_trigger_pct", 0.01)
            threshold = self.entry_price * (
                1 + trigger_pct if self.side == "buy" else 1 - trigger_pct
            )
            if not self.triggered:
                if (self.side == "buy" and current_price > threshold) or (
                    self.side == "sell" and current_price < threshold
                ):
                    self.sl_price = self.entry_price
                    self.triggered = True
                    updated = True

        if updated:
            self.logger.info(
                f"[Trailing SL Updated] Order {self.order_id} new SL: {self.sl_price:.2f}"
            )

        return self.sl_price

    def is_stop_hit(self, ltp):
        if self.side == "buy":
            return ltp <= self.sl_price
        else:
            return ltp >= self.sl_price
