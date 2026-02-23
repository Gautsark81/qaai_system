from core.safety.kill_switch import GlobalKillSwitch
from core.paper.paper_executor import PaperExecutor

def test_kill_switch():
    executor = PaperExecutor()
    GlobalKillSwitch.activate("test")

    try:
        executor.execute("STRAT", "RELIANCE", "BUY", 10, 2500)
    except RuntimeError as e:
        print("PASS:", e)

if __name__ == "__main__":
    test_kill_switch()
