def broker_rejection_spike(reject_rate):
    return reject_rate > 0.15


def kill_switch_triggered():
    return True
