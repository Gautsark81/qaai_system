# File: core/strategy_factory/promotion/state_machine/promotion_state.py

from enum import Enum


class PromotionState(str, Enum):
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    TINY_LIVE = "TINY_LIVE"
    LIVE = "LIVE"
