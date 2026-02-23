"""
Backwards compatibility shim for ExplainabilityLogger.

Originally defined under qaai_system.screener.explainability,
now lives in qaai_system.utils.explainability.
"""

from qaai_system.utils.explainability import ExplainabilityLogger

__all__ = ["ExplainabilityLogger"]
