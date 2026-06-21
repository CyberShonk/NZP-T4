# Current status

Updated: 2026-06-20

## Repository foundation

- Repository layout and public project policy: **implemented**.
- Local private context and Git safeguards: **installed in the supplied local workspace, not tracked**.
- Public remote: **not configured**.
- Initial commit: **not created**.
- Upstream engine/gameplay forks and exact commit pins: **not established**.

## Implemented

### Package inspector v0.1.0

- Read-only directory inspection.
- Read-only ZIP and ZIP-compatible IWD inspection.
- SHA-256 package and file fingerprints.
- Deterministic normalized inventory.
- Archive path, absolute-path, drive-path, symlink, encrypted-entry, duplicate-path, size, count, and compression-ratio checks.
- Conservative file classification and format counts.
- Native/executable dependency warnings.
- Name-only framework hints that do not imply compatibility.
- Versioned `compatibility_report.json` schema.
- Standard-library unit tests and original redistributable fixture.

## Not implemented

- Android project, APK, or ARM64 build.
- NZ:P engine or QuakeC fork integration.
- Stock NZ:P map boot on Android.
- Package extraction or conversion.
- FastFile parsing.
- D3DBSP loading or translation.
- GSC execution or translation.
- Runtime compatibility shims.
- Playable World at War custom-map support.

## Validation baseline

Run:

```bash
./tools/check-project.sh
```

A capability is not supported until source, tests, and a repeatable runtime result establish it.

## Next measurable action

Create and pin explicit forks of the NZ:P FTEQW engine and QuakeC repositories, then perform a source-grounded ARM64 Android build spike. The result must either boot one native NZ:P map with sanitized logs or document the exact reproducible blocker.
