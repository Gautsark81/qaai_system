import sys
from .phase_guard import enforce_phase_guard


def main():
    try:
        enforce_phase_guard()
    except Exception as e:
        print(f"[PHASE GUARD FAIL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
