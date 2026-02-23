# ======================================================
# Strategy Factory Exceptions (CANONICAL / STABLE)
# ======================================================

class StrategyFactoryError(Exception):
    """
    Base exception for all strategy-factory-level failures.

    Scope:
    - Identity
    - Governance
    - Lifecycle
    - Promotion / Demotion

    NEVER:
    - Market errors
    - Broker errors
    - Execution transport errors
    """
    pass


# -------------------------------
# Identity & Validation
# -------------------------------

class StrategyValidationError(StrategyFactoryError):
    """
    Raised when a strategy definition violates
    hard deterministic constraints.

    Examples:
    - Invalid AlphaGenome
    - Missing required fields
    - Unsupported configuration
    """
    pass


class DuplicateStrategyError(StrategyFactoryError):
    """
    Raised when attempting to register a strategy whose
    DNA already exists.

    Enforces:
    - Deterministic identity
    - Registry immutability
    - Audit safety
    """
    pass


class StrategyGenerationError(StrategyFactoryError):
    """
    Raised when system-driven strategy generation fails.

    Indicates:
    - Internal system fault
    - NOT a strategy fault
    """
    pass


# -------------------------------
# Governance & Execution
# -------------------------------

class ExecutionNotAllowed(StrategyFactoryError):
    """
    Raised when a strategy is NOT permitted to execute.

    Examples:
    - Phase-B advisory mode
    - Not promoted to LIVE
    - Strategy frozen / killed
    - Global kill switch
    """
    pass


class PhaseConstraintViolation(StrategyFactoryError):
    """
    Raised when an operation violates the
    current system phase contract.
    """
    pass


# -------------------------------
# Lifecycle
# -------------------------------

class IllegalLifecycleTransition(StrategyFactoryError):
    """
    Raised when an invalid lifecycle transition
    is attempted.

    Examples:
    - CREATED → LIVE
    - KILLED → PAPER
    - RETIRED → LIVE

    Enforces:
    - Strict lifecycle DAG
    - Full auditability
    """
    pass


class TerminalStateViolation(StrategyFactoryError):
    """
    Raised when attempting to mutate a terminal state
    such as KILLED or RETIRED.
    """
    pass
