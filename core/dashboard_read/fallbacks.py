from core.dashboard_read.snapshot import (
    SystemHealth,
    DataFeedHealth,
    BrokerHealth,
    MarketState,
    MarketRegime,
    ExtremeEventState,
    ScreeningState,
    WatchlistState,
    StrategyFactoryState,
    PipelineState,
    StrategyState,
    ExecutionState,
    RiskState,
    CapitalState,
    ShadowState,
    PaperState,
    IncidentState,
    ComplianceState,
    OpsState,
)

# ---------------------------------------------------------------------
# SYSTEM HEALTH
# ---------------------------------------------------------------------

def fallback_system_health() -> SystemHealth:
    return SystemHealth(
        data_feeds=[],
        broker=BrokerHealth(
            connected=False,
            rate_limit_state="UNKNOWN",
            last_error="SOURCE_UNAVAILABLE",
        ),
        services={},
        alerts_active=True,
    )


# ---------------------------------------------------------------------
# MARKET
# ---------------------------------------------------------------------

def fallback_market_state() -> MarketState:
    return MarketState(
        regime=MarketRegime(
            volatility="UNKNOWN",
            liquidity="UNKNOWN",
            stress_level="UNKNOWN",
        ),
        extreme_event=ExtremeEventState(
            active=False,
            classification=None,
        ),
        session="UNKNOWN",
    )


# ---------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------

def fallback_pipeline_state() -> PipelineState:
    return PipelineState(
        screening=ScreeningState(
            symbols_seen=0,
            passed=0,
            rejected_by_reason={},
        ),
        watchlist=WatchlistState(
            added=0,
            removed=0,
            active=0,
        ),
        strategy_factory=StrategyFactoryState(
            generated=0,
            active=0,
            retired=0,
        ),
    )


# ---------------------------------------------------------------------
# STRATEGY
# ---------------------------------------------------------------------

def fallback_strategy_state() -> StrategyState:
    return StrategyState(
        active=[],
        at_risk=[],
        retiring=[],
        retired=[],
    )


# ---------------------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------------------

def fallback_execution_state() -> ExecutionState:
    return ExecutionState(
        intents_created=0,
        intents_blocked=0,
        blocked_reasons={},
        positions=[],
        fills=0,
    )


# ---------------------------------------------------------------------
# RISK & CAPITAL
# ---------------------------------------------------------------------

def fallback_risk_state() -> RiskState:
    return RiskState(
        checks_passed=0,
        checks_failed=0,
        dominant_violation=None,
        freeze_active=False,
    )


def fallback_capital_state() -> CapitalState:
    return CapitalState(
        total_capital=0.0,
        allocated_capital=0.0,
        free_capital=0.0,
        utilization_ratio=0.0,
        throttle_active=False,
    )


# ---------------------------------------------------------------------
# SHADOW & PAPER
# ---------------------------------------------------------------------

def fallback_shadow_state() -> ShadowState:
    return ShadowState(
        enabled=False,
        decisions_mirrored=0,
        divergences_detected=0,
        last_divergence_reason=None,
    )


def fallback_paper_state() -> PaperState:
    return PaperState(
        pnl=0.0,
        drawdown=0.0,
        active_positions=0,
    )


# ---------------------------------------------------------------------
# INCIDENTS & COMPLIANCE
# ---------------------------------------------------------------------

def fallback_incident_state() -> IncidentState:
    return IncidentState(
        open_incidents=0,
        total_incidents=0,
        last_incident_type=None,
        capital_frozen=False,
    )


def fallback_compliance_state() -> ComplianceState:
    return ComplianceState(
        audit_packs_ready=False,
        last_bundle_hash=None,
        notarized=False,
        regulator_ready=False,
    )


# ---------------------------------------------------------------------
# OPS (CRITICAL — D-3 GUARANTEE)
# ---------------------------------------------------------------------

def fallback_ops_state() -> OpsState:
    """
    Ops fallback must ALWAYS be schema-perfect.
    No inference. No degradation logic. Pure state.
    """
    return OpsState(
        human_control=True,
        takeover_active=False,
        succession_mode="UNKNOWN",
        runbook_link=None,
    )
