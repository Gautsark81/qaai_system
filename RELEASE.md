Release procedure (Phase 1)
1. Ensure tests pass locally:
   pytest -q

2. Commit changes on branch:
   git checkout -b feature/amats-phase1
   git add data/tick_store.py tests CHANGELOG.md RELEASE.md requirements-dev.txt .github/workflows/ci.yml
   git commit -m "feat(tick_store): supercharged TickStore; fix :memory: schema bug, add WAL, retries, pruning, parquet export"
   git push -u origin feature/amats-phase1

3. Open PR using PR_BODY.md as description and request reviewers.

4. After PR approved, create tag:
   git tag -a v0.1.0-phase1 -m "AMATS Phase 1: TickStore overhaul"
   git push origin v0.1.0-phase1
