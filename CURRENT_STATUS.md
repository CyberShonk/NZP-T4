# Current status

Updated: 2026-06-21

## Repository foundation

- Public umbrella repository and `main` branch: **established**.
- Local private context and Git safeguards: **installed locally and excluded from public Git**.
- Package inspector foundation: **implemented and validated**.
- Upstream source-audit baseline: **recorded**.
- Linux x86_64 upstream baseline: **reproduced successfully**.
- Engine and gameplay forks: **not created**.

## Verified upstream baseline

The source audit records these exact upstream revisions:

- NZ:P hub: `nzp-team/nzportable` at `648a1bc56b8a4de4c86a7fca2e1d76308dcd4ae5`.
- Runtime assets: `nzp-team/assets` at `5c3527c0e60381db3afb2489bc882a44b76b9daf`.
- Desktop/FTE engine: `nzp-team/fteqw` at `f68a2b547d2dc4bf6886b922baa1bff487cc5038`.
- QuakeC gameplay: `nzp-team/quakec` at `6613eb72359d1244e6034d31c3d07f78c1cf9b6f`.

The engine, gameplay, and asset revisions have now been demonstrated as a compatible Linux x86_64 runtime baseline when the assets are obtained from the matching official PC release archive.

Confirmed findings:

- The hub coordinates releases and assembles separately published engine, gameplay, and asset archives.
- The assets repository contains runtime data required to play NZ:P.
- The matching `newest` asset release tag resolved to the audited asset commit during the baseline test.
- The official PC asset archive contained 19 compiled BSP maps.
- The audited QuakeC revision compiled successfully with Python 3.12 in an isolated environment.
- The audited FTEQW revision compiled successfully in a Fedora 42 Toolbox environment.
- The resulting Linux x86_64 engine initialized SDL audio and OpenGL and loaded stock map `4all` into an active local session.
- Directly copying the asset source checkout was insufficient because it did not provide the compiled BSP release artifacts.
- FTEQW contains Android-related source and legacy build machinery.
- No supported, modern, reproducible NZ:P Android build has been verified.
- No root-level Git submodules were found in the four audited repositories.

See [docs/LINUX_DESKTOP_BASELINE.md](docs/LINUX_DESKTOP_BASELINE.md) for commands, hashes, results, and reproducibility notes.

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

### Linux x86_64 upstream baseline

- Pinned QuakeC build: **successful**.
- Pinned FTEQW Linux x86_64 build: **successful**.
- Matching official PC runtime-data assembly: **successful**.
- Direct stock-map boot using `4all`: **successful**.
- Engine SHA-256: `567de5a44aed4ee285a172879498a8c41c7675e6cd4d428ffa456d205081948f`.

## Not implemented

- NZ:P T4 Android project, APK, or verified ARM64 build.
- NZ:P engine or QuakeC fork integration.
- Automated or supported desktop packaging in this repository.
- Stock NZ:P map boot on Android.
- Package extraction or conversion.
- FastFile parsing.
- D3DBSP loading or translation.
- GSC execution or translation.
- Runtime compatibility shims.
- Playable World at War custom-map support.

## Known baseline limitations

- The matching PC release archive was required for compiled BSP maps; copying only the pinned asset source tree did not produce a playable runtime.
- The release archive SHA-256 has not yet been recorded in public documentation.
- The corrected runtime was verified through direct `+map 4all` launch. Menu-based map selection was not separately re-verified after correcting the asset assembly.
- The successful map session emitted non-blocking `PF_fclose` and unprecached-sound warnings.
- Building FTEQW from a physical path containing whitespace broke an upstream dependency include path. The successful build used a whitespace-free path.
- The pinned QuakeC Python dependency set did not install under Python 3.14; the successful build used Python 3.12.

## Validation baseline

Run:

```bash
./tools/check-project.sh
```

A capability is not supported until source, tests, and a repeatable runtime result establish it.

## Next measurable action

Audit and attempt the legacy Android build path at the pinned FTEQW revision without creating a fork. Record the existing Android source layout, required SDK and NDK generations, obsolete assumptions, first reproducible failure, and the smallest source or build-system change required to proceed.

Do not claim a usable Android build until an APK or equivalent runnable artifact is produced and tested on ARM64 Android hardware.
