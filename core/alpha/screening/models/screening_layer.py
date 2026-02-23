from enum import Enum


class ScreeningLayer(str, Enum):
    DATA_INTEGRITY = "data_integrity"
    LIQUIDITY_SURVIVABILITY = "liquidity_survivability"
    REGIME_ADMISSIBILITY = "regime_admissibility"
    STATISTICAL_ILLUSION = "statistical_illusion"
    FLOW_AUTHENTICITY = "flow_authenticity"
    CORRELATION_RISK = "correlation_risk"
    HORIZON_MISMATCH = "horizon_mismatch"
    MACRO_FRAGILITY = "macro_fragility"
    OPPORTUNITY_CONFIRMATION = "opportunity_confirmation"
    CROSS_FACTOR_FRAGILITY = "cross_factor_fragility"
