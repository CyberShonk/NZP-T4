# Public architecture

## Current component

The current repository contains a read-only package inspector:

```text
user-selected folder, ZIP, or IWD
  -> metadata and path validation
  -> bounded hashing and inventory
  -> conservative classification
  -> structured compatibility report
```

The inspector never executes or extracts imported content.

## Future integration boundary

Future work is expected to connect three separately testable areas:

1. Android application and lifecycle integration.
2. NZ:P engine and QuakeC gameplay forks.
3. Import-time compatibility tooling and reports.

Exact runtime, translation, and map-specific strategies remain research work until verified by source and legal test fixtures.

## Design rules

- Imported packages are untrusted and read-only.
- Recognition is not compatibility.
- Unsupported behavior must be explicit.
- User-local content is not automatically redistributable.
- Android support requires repeatable device evidence.
- Upstream source and asset licenses must remain intact.
