# scripts/test_dhan.py
from providers.dhan_client import DhanClient


def main():
    try:
        c = DhanClient()
    except Exception as e:
        print("Failed to init DhanClient:", e)
        return

    try:
        pos = c.get_positions()
        print("Positions call succeeded. Sample:", type(pos))
    except Exception as e:
        print("Positions call failed. Error:", e)


if __name__ == "__main__":
    main()
