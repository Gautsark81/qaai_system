# tools/phase_rules.py

def is_allowed(src_phase, dst_phase):
    # Execution → execution (only forward)
    if src_phase.isdigit() and dst_phase.isdigit():
        return int(dst_phase) <= int(src_phase)

    # Architecture → architecture (only backward)
    if src_phase.isalpha() and dst_phase.isalpha():
        return ord(dst_phase) <= ord(src_phase)

    # Execution importing architecture: allowed
    if src_phase.isdigit() and dst_phase.isalpha():
        return True

    # Architecture importing execution: forbidden
    if src_phase.isalpha() and dst_phase.isdigit():
        return False

    return False
