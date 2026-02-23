_OPERATORS = {
    "add": 2,
    "sub": 2,
    "mul": 2,
    "div": 2,
    "gt": 2,
    "lt": 2,
}

def arity(op: str) -> int:
    if op not in _OPERATORS:
        raise ValueError(f"Unknown operator: {op}")
    return _OPERATORS[op]
