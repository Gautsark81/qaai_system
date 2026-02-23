FORBIDDEN_STATES = {
    "RESURRECTION_CANDIDATE",
    "REVIVAL_SHADOW",
    "REVIVAL_PAPER",
}


def assert_resurrection_execution_block(record):
    if record.state in FORBIDDEN_STATES:
        raise PermissionError("Execution blocked during resurrection flow")
