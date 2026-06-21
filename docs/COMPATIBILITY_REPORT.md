# Compatibility report

The inspector writes JSON conforming to `schemas/compatibility-report.schema.json`.

Core fields include:

- schema and inspector version;
- package display name, type, size, and SHA-256;
- deterministic package fingerprint;
- inspection completion and safety state;
- normalized inventory with per-file hashes;
- file-category and extension counts;
- framework name hints with evidence paths;
- warnings and blocking findings;
- a conservative capability tier.

## Capability tier in v0.1.0

- `0`: the package was safely inventoried. This does not mean it is loadable or playable.
- `U`: inspection was blocked or incomplete.

Later tiers require runtime evidence and are intentionally not assigned by the current inspector.
