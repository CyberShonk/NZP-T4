# Upstream components

NZ:P is assembled from separate source and runtime-data repositories. NZ:P T4 records exact source-audit pins so later build and compatibility work can be reproduced.

## Audited components

| Component | Repository | Default branch | Audit pin | Role | Root license status |
|---|---|---|---|---|---|
| Hub/releases | `nzp-team/nzportable` | `main` | `648a1bc56b8a4de4c86a7fca2e1d76308dcd4ae5` | Project hub, issues, and release assembly | No root license file observed |
| Runtime assets | `nzp-team/assets` | `main` | `5c3527c0e60381db3afb2489bc882a44b76b9daf` | Maps, textures, sounds, platform data, and selected source assets | `LICENSE.md`, CC BY-SA 4.0 |
| Engine | `nzp-team/fteqw` | `master` | `f68a2b547d2dc4bf6886b922baa1bff487cc5038` | Desktop Linux, Windows, macOS, and Web engine | GPL-2.0 root license plus bundled-component notices |
| Gameplay | `nzp-team/quakec` | `main` | `6613eb72359d1244e6034d31c3d07f78c1cf9b6f` | Gameplay, server logic, shared definitions, and FTE CSQC | GPL-2.0 |

These pins identify the revisions inspected during the audit. They are not yet a proven mutually compatible build or release tuple.

## Repository relationships

The hub does not vendor the engine, gameplay code, or assets as submodules. Its nightly assembly script watches moving upstream branches, downloads moving `newest` or `bleeding-edge` release archives, and combines:

- a platform asset archive such as `pc-nzp-assets.zip`;
- compiled QuakeC such as `fte-nzp-qc.zip`;
- a platform engine archive such as `pc-nzp-linux64.zip`.

No root-level Git submodules or gitlinks were found in the four audited repositories.

## Desktop engine build evidence

The FTEQW README documents a make-based build and recommends the project Docker environment. Its quick-start path says `source/engine`, but the audited repository exposes the engine directory at `engine/`.

The audited Linux x86_64 helper script, `tools/build-nzp-linux64.sh`, changes to `engine/` and invokes the equivalent of:

```bash
export CC=x86_64-linux-gnu-gcc
export STRIP=x86_64-linux-gnu-strip
make makelibs FTE_TARGET=SDL2
make m-rel FTE_TARGET=SDL2 FTE_CONFIG=nzportable -j32
```

It then renames the release binary to `nzportable64-sdl`. These commands are source-confirmed but have not yet been reproduced by NZ:P T4.

## QuakeC build evidence

The gameplay repository requires Python 3.7 or newer for hash-table generation and includes platform-specific FTEQCC binaries and compiler scripts. On GNU/Linux, the source-confirmed entry point is:

```bash
./tools/qc-compiler-gnu.sh
```

The script generates a hash table and builds FTE CSQC, FTE SSQC, FTE MenuQC, and standard/Vril SSQC outputs under `build/`.

The upstream release workflow downloads Python requirements from the moving `main` branch of `nzp-team/QCHashTableGenerator`. That dependency is not revision-pinned and must be captured before claiming a fully reproducible QuakeC build.

## Runtime data

The assets repository states that it stores the game data required to play NZ:P, including maps, textures, and sounds. Platform archives are assembled from shared `common/` data and platform-specific directories. The audited root license is CC BY-SA 4.0.

Redistribution must preserve the applicable attribution and ShareAlike terms and any narrower per-file notices. NZ:P T4 does not currently copy or redistribute these assets.

## Fork policy

Do not copy upstream source into the umbrella repository.

- **Engine:** a separate FTEQW fork is likely because NZ:P T4 requires maintained Android work that upstream does not support. Create it only after reproducing the pinned desktop baseline and identifying the first required source change.
- **Gameplay:** use a pinned upstream QuakeC checkout initially. Create a separate gameplay fork only when a concrete compatibility change requires modifying gameplay, CSQC, server, or shared source.
- **Assets:** do not fork merely to obtain runtime data. First reproduce assembly from the pinned source and preserve all applicable attribution and license information.

## Evidence classification

- Repository roles, default branches, audit pins, root trees, license-file paths, and build-script contents: **verified through technical research**.
- Compatibility of the four audit pins as one working runtime: **unverified**.
- Desktop build and stock-map boot at these pins: **planned**.
- Separate engine fork: **planned after baseline reproduction**.
- Separate gameplay fork: **deferred**.
