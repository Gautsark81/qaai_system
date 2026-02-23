# Changelog

## [v0.1.0-phase1] - YYYY-MM-DD
### Added
- Supercharged TickStore: robust connection handling, WAL settings, retries on DB busy, auto-prune option.
- export_to_parquet to extract flattened raw_json to parquet.
- Tests ensuring :memory: behavior and basic store features.

### Fixed
- Fixed `no such table: ticks` in tests using SQLite in-memory DB by ensuring schema creation uses the same connection as subsequent writes.
