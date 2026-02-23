import inspect
import core.execution.broker_capabilities.contracts as contracts
import core.execution.broker_capabilities.validator as validator


def test_no_execution_functions_present():
    forbidden = {"execute", "place_order", "send", "submit"}

    for module in (contracts, validator):
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                for word in forbidden:
                    assert word not in name.lower()
