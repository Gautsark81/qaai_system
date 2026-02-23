# Secrets & Configuration Policy

## Secrets
- Stored only in OS secret store / vault
- Never committed
- Never logged
- Never exposed to ML layer

Examples:
- Broker API keys
- Database credentials

## Config Layers
1. defaults.yaml (safe, committed)
2. env.yaml (environment specific)
3. secrets (external only)

## Prohibited
- Hardcoded secrets
- ENV var fallbacks in LIVE
- Dynamic config mutation at runtime
