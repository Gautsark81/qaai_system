# scripts/test_dhan_ws.py
"""
Simple test: start the WS consumer in dry-run mode for N seconds and assert no exceptions.
"""
import subprocess
import time
import sys


def run_for(seconds=10):
    print("Starting WS consumer in dry-run mode for", seconds, "seconds")
    proc = subprocess.Popen(
        [sys.executable, "ingestion/dhan_ws.py", "--dry-run"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        t0 = time.time()
        while time.time() - t0 < seconds:
            line = proc.stdout.readline()
            if line:
                print(line.strip())
    finally:
        proc.terminate()
        proc.wait()
        print("Done.")


if __name__ == "__main__":
    run_for(8)
