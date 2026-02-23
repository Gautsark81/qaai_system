import inspect
import ast

import core.dashboard_read.providers as providers


FORBIDDEN_NODES = (
    ast.If,
    ast.Compare,
    ast.BinOp,
    ast.Call,
)


def test_providers_do_not_compute():
    """
    Providers must not contain logic.
    They may only copy values.
    """

    for name in dir(providers):
        if name.startswith("_") or name == "tests":
            continue

        module = getattr(providers, name)

        if not hasattr(module, "__file__"):
            continue

        if "providers/tests" in module.__file__:
            continue


        source = inspect.getsource(module)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                raise AssertionError(
                    f"Logic detected in provider {module.__name__}"
                )
