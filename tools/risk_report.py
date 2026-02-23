import json
from collections import Counter

data = json.loads(open("project_super_status.json").read())

risk_counter = Counter()
by_file = []

for f in data["files"].values():
    for r in f.get("risks", []):
        risk_counter[r] += 1
        by_file.append((r, f["path"]))

print("🚨 RISK SUMMARY\n")
for r, c in risk_counter.items():
    print(f"{r}: {c}")

print("\n📂 FILES\n")
for r, p in by_file:
    print(f"{r:20} {p}")
