import pytest
from core.runtime.runtime_contract import RuntimeContract, RuntimeContractViolation


def test_runtime_contract_blocks_mutation():
    initial = {
        "capital_limits": 100,
        "risk_limits": 10,
        "strategy_definitions": ["A"],
    }

    contract = RuntimeContract(initial)

    mutated = dict(initial)
    mutated["risk_limits"] = 20

    with pytest.raises(RuntimeContractViolation):
        contract.validate(mutated)
