# File: core/strategy_factory/promotion/promotion_reason.py

from enum import Enum


class PromotionReason(str, Enum):
    SSR_ABOVE_THRESHOLD = "SSR_ABOVE_THRESHOLD"
    SSR_BELOW_THRESHOLD = "SSR_BELOW_THRESHOLD"
