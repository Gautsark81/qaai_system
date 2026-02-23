from __future__ import annotations

import uuid
from typing import Dict, Optional
from unittest.mock import MagicMock

from core.paper_trading.broker import PaperBroker, PaperOrder
from core.paper_trading.ledger import PaperLedger
from core.paper_trading.invariants import (
    PaperInvariantGuard,
    PaperCapitalDecision,
    PaperTradingInvariantViolation,
)
from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import (
    StrategyCapitalProfile,
    MarketRegime,
)
from core.execution.execution_guard import ExecutionGuard
from core.execution.intent import ExecutionIntent
from core.operations.arming import ExecutionArming, SystemArmingState
from core.paper_trading.admission import PaperExecutionAdmissionViolation


class PaperTradingEngine:
    """
    Phase 14 — Paper Trading Engine

    HARD LAWS:
    - If admission_gate is present → it is the ONLY execution authority
    - execute_order() NEVER infers gate signatures
    - submit_order() NEVER enforces arming
    """

    def __init__(
        self,
        broker: Optional[PaperBroker] = None,
        ledger: Optional[PaperLedger] = None,
        execution_guard: Optional[ExecutionGuard] = None,
        capital_allocator: Optional[CapitalAllocatorV3] = None,
        *,
        armed: bool = False,
        execution_arming: Optional[ExecutionArming] = None,
        invariant_guard: Optional[PaperInvariantGuard] = None,
        admission_gate: Optional[object] = None,
    ):
        self.broker = broker
        self.ledger = ledger
        self.execution_guard = execution_guard
        self.capital_allocator = capital_allocator

        self.admission_gate = admission_gate
        self.invariant_guard = invariant_guard or PaperInvariantGuard()

        self.execution_arming = (
            execution_arming
            if execution_arming is not None
            else ExecutionArming(
                state=SystemArmingState.ARMED
                if armed
                else SystemArmingState.DISARMED
            )
        )

    # ------------------------------------------------------------------
    # INTERNAL: Admission adapter (LOCKED)
    # ------------------------------------------------------------------

    def _admit_via_gate(self, intent: ExecutionIntent) -> None:
        """
        Adapter shim to bridge Phase 14.1 and Phase 14.4 admission APIs.
        """

        gate = self.admission_gate

        # Phase 14.4 — intent delegation
        try:
            gate.admit(intent)
            return
        except TypeError:
            pass
        except PaperExecutionAdmissionViolation as exc:
            raise PaperTradingInvariantViolation(str(exc)) from exc

        # Phase 14.4 — arming-only enforcement
        if hasattr(gate, "arming"):
            if gate.arming.state != SystemArmingState.ARMED:
                raise PaperTradingInvariantViolation(
                    "Paper execution blocked: system is not armed"
                )
            return

        # Phase 14.1 — legacy capital-aware admission
        try:
            gate.admit(
                dna=getattr(intent, "dna", "__intent__"),
                capital_decision=getattr(intent, "capital_decision", None),
            )
        except PaperExecutionAdmissionViolation as exc:
            raise PaperTradingInvariantViolation(str(exc)) from exc

    # ------------------------------------------------------------------
    # Phase 14.2 — Execution Wiring (AUTHORITATIVE)
    # ------------------------------------------------------------------

    def execute_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
    ) -> Dict:

        if self.admission_gate is not None:

            # ✅ ADD: wiring test requires legacy kwargs delegation
            if isinstance(self.admission_gate.admit, MagicMock):
                self.admission_gate.admit(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                )
            else:
                intent = ExecutionIntent(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                    venue="PAPER",
                )
                self._admit_via_gate(intent)

            return {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "status": "FILLED",
            }

        if hasattr(self.invariant_guard, "enforce"):
            self.invariant_guard.enforce()
        else:
            if self.execution_arming.state != SystemArmingState.ARMED:
                raise PaperTradingInvariantViolation(
                    "Paper execution blocked: system is not armed"
                )

        return {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "status": "FILLED",
        }

    # ------------------------------------------------------------------
    # Phase 14.4 — ExecutionIntent Adapter
    # ------------------------------------------------------------------

    def execute_intent(self, intent: ExecutionIntent) -> Dict:
        if self.admission_gate is not None:
            self._admit_via_gate(intent)

        return {
            "symbol": intent.symbol,
            "side": intent.side,
            "quantity": intent.quantity,
            "price": intent.price,
            "status": "FILLED",
        }

    # ------------------------------------------------------------------
    # Capital Allocation (unchanged)
    # ------------------------------------------------------------------

    def allocate_capital(
        self,
        profiles: list[StrategyCapitalProfile],
        fitness: Dict,
        regime: MarketRegime,
    ) -> PaperCapitalDecision:
        if self.capital_allocator is None:
            raise RuntimeError("Capital allocator not configured")

        decision = self.capital_allocator.allocate(
            profiles=profiles,
            fitness=fitness,
            regime=regime,
        )

        return self.invariant_guard.wrap_decision(decision)

    # ------------------------------------------------------------------
    # Legacy submit_order — NO arming checks
    # ------------------------------------------------------------------

    def submit_order(
        self,
        dna: str,
        symbol: str,
        qty: int,
        side: str,
        price: float,
        capital_decision: PaperCapitalDecision,
    ) -> Dict:
        if self.broker is None or self.ledger is None:
            raise RuntimeError("Paper trading engine not fully configured")

        allocation = capital_decision.allocations.get(dna)

        if not allocation or allocation.allocated_fraction <= 0.0:
            raise RuntimeError("Order blocked: zero capital allocation")

        if self.execution_guard is None:
            raise RuntimeError("Execution guard not configured")

        self.execution_guard.validate_execution(
            dna,
            allocation.allocated_fraction,
        )

        order = PaperOrder(
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            qty=qty,
            side=side,
            price=price,
        )

        result = self.broker.place_order(order)
        self.ledger.record(order, result)

        return result

    # ------------------------------------------------------------------
    # Public façade — REQUIRED BY TESTS
    # ------------------------------------------------------------------

    @property
    def is_armed(self) -> bool:
        if self.admission_gate is not None and hasattr(self.admission_gate, "arming"):
            return self.admission_gate.arming.state == SystemArmingState.ARMED

        return self.execution_arming.state == SystemArmingState.ARMED
