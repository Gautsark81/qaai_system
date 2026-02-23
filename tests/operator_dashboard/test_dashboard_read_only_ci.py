import inspect
import modules.operator_dashboard as dashboard


FORBIDDEN_IMPORTS = {
    "core.execution",
    "core.order",
    "core.broker",
    "core.trade",
}


def test_dashboard_is_read_only():
    for name, module in dashboard.__dict__.items():
        if not inspect.ismodule(module):
            continue

        src = inspect.getsource(module)

        for forbidden in FORBIDDEN_IMPORTS:
            assert forbidden not in src, (
                f"Forbidden execution import detected: {forbidden}"
            )
