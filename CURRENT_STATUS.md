# Current status

Updated: 2026-06-21

## Repository foundation

- Public umbrella repository and `main` branch: **established**.
- Local private context and Git safeguards: **installed locally and excluded from public Git**.
- Package inspector foundation: **implemented and validated**.
- Upstream source-audit baseline: **recorded**.
- Engine and gameplay forks: **not created**.

## Verified upstream audit baseline

The source audit records these exact upstream revisions:

- NZ:P hub: `nzp-team/nzportable` at `648a1bc56b8a4de4c86a7fca2e1d76308dcd4ae5`.
- Runtime assets: `nzp-team/assets` at `5c3527c0e60381db3afb2489bc882a44b76b9daf`.
- Desktop/FTE engine: `nzp-team/fteqw` at `f68a2b547d2dc4bf6886b922baa1bff487cc5038`.
- QuakeC gameplay: `nzp-team/quakec` at `6613eb72359d1244e6034d31c3d07f78c1cf9b6f`.

These revisions are source-audit pins. They are not yet a demonstrated compatible build tuple.

Confirmed findings:

- The hub coordinates releases and assembles separately published engine, gameplay, and asset archives.
- The assets repository contains runtime data required to play NZ:P.
- The engine and gameplay repositories provide desktop build machinery.
- FTEQW contains Android-related source and legacy build machinery.
- No supported, modern, reproducible NZ:P Android build has been verified.
- No root-level Git submodules were found in the four audited repositories.

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

- NZ:P T4 Android project, APK, or verified ARM64 build.
- NZ:P engine or QuakeC fork integration.
- Reproduced desktop engine/gameplay/runtime assembly at the audit pins.
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

Reproduce one Linux x86_64 desktop baseline from the audited FTEQW and QuakeC revisions, assemble it with the audited runtime assets, and boot one stock NZ:P map. Record exact commands, output hashes, and sanitized logs. Do not create an engine or gameplay fork until this baseline establishes which source changes are actually required.
