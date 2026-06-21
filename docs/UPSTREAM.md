# Upstream components

NZ:P is assembled from separate source and runtime-data repositories. NZ:P T4 records exact pins so later build and compatibility work can be reproduced.

## Audited components

| Component | Repository | Default branch | Audit pin | Role | Root license status |
|---|---|---|---|---|---|
| Hub/releases | `nzp-team/nzportable` | `main` | `648a1bc56b8a4de4c86a7fca2e1d76308dcd4ae5` | Project hub, issues, and release assembly | No root license file observed |
| Runtime assets | `nzp-team/assets` | `main` | `5c3527c0e60381db3afb2489bc882a44b76b9daf` | Maps, textures, sounds, platform data, and selected source assets | `LICENSE.md`, CC BY-SA 4.0 |
| Engine | `nzp-team/fteqw` | `master` | `f68a2b547d2dc4bf6886b922baa1bff487cc5038` | Desktop Linux, Windows, macOS, and Web engine | GPL-2.0 root license plus bundled-component notices |
| Gameplay | `nzp-team/quakec` | `main` | `6613eb72359d1244e6034d31c3d07f78c1cf9b6f` | Gameplay, server logic, shared definitions, and FTE CSQC | GPL-2.0 |

These revisions were inspected during the source audit. The engine, gameplay, and asset revisions were subsequently reproduced as a working Linux x86_64 runtime baseline when the assets were taken from the matching official PC release archive.

## Repository relationships

The hub does not vendor the engine, gameplay code, or assets as submodules. Its nightly assembly script watches moving upstream branches, downloads moving `newest` or `bleeding-edge` release archives, and combines:

- a platform asset archive such as `pc-nzp-assets.zip`;
- compiled QuakeC such as `fte-nzp-qc.zip`;
- a platform engine archive such as `pc-nzp-linux64.zip`.

No root-level Git submodules or gitlinks were found in the four audited repositories.

## Reproduced desktop engine build

The FTEQW README documents a make-based build and recommends the project Docker environment. Its quick-start path says `source/engine`, but the audited repository exposes the engine directory at `engine/`.

The Linux x86_64 baseline was reproduced in a Fedora 42 Toolbox using a whitespace-free checkout path. The effective build was:

```bash
cd fteqw/engine
export CC=gcc
export CXX=g++
export STRIP=strip
export PKG_CONFIG=pkg-config
make makelibs FTE_TARGET=SDL2
make m-rel FTE_TARGET=SDL2 FTE_CONFIG=nzportable -j"$(nproc)"
```

The build produced:

```text
release/nzportable-sdl2
release/nzportable-sdl2.db
```

The stripped executable was a dynamically linked Linux x86_64 ELF with this SHA-256:

```text
567de5a44aed4ee285a172879498a8c41c7675e6cd4d428ffa456d205081948f
```

No unresolved runtime libraries were reported by `ldd`. Its observed direct dynamic dependencies were SDL2, libc, libm, and the system ELF loader.

A checkout path containing whitespace caused an upstream dependency include path to be truncated during `makelibs`. The successful reproduction therefore used a physical path without spaces.

## Reproduced QuakeC build

The gameplay repository includes platform-specific FTEQCC binaries and compiler scripts. On GNU/Linux, the entry point is:

```bash
./tools/qc-compiler-gnu.sh
```

The pinned dependency set did not install under the host's Python 3.14. The successful build used an isolated Python 3.12 environment with:

```text
colorama==0.4.6
fastcrc==0.3.0
pandas==2.1.4
```

The successful FTE outputs and SHA-256 values were:

| Output | SHA-256 |
|---|---|
| `csprogs.dat` | `740097be8470c3d90c028dab963d797e1b8af296537d3ba5dd53256baefbb543` |
| `csprogs.lno` | `42d6a62abc67b1eb67466551aa0cfaed3dd00b6756a832bed41d78a8ad32fd3d` |
| `menu.dat` | `360701578139138a43e3beb3066215a737d30f94b9a95032936b30089e4c16d4` |
| `qwprogs.dat` | `93c97b487c42a6611b611119b794eb1ac64ce6bae07855e542c84205a25b7a33` |

The upstream release workflow still downloads Python requirements from the moving `main` branch of `nzp-team/QCHashTableGenerator`. The baseline captured the resolved package versions, but that upstream workflow dependency remains unpinned.

## Runtime data and assembly

The assets repository stores game data required to play NZ:P, including maps, textures, and sounds. Platform archives are assembled from shared `common/` data and platform-specific directories.

A direct copy from the pinned asset source checkout produced a runtime tree but did not include the compiled BSP maps referenced by the menu. The engine initialized, but map loads returned to the menu with missing-file messages.

The official `newest` asset release tag resolved to the exact audited asset commit during the test:

```text
5c3527c0e60381db3afb2489bc882a44b76b9daf
```

Its `pc-nzp-assets.zip` archive contained 19 compiled BSP maps, including `4all.bsp`, `lexi_overlook.bsp`, and `nzp_warehouse2.bsp`. Combining that archive with the reproduced QuakeC outputs and engine executable produced a runnable Linux x86_64 tree.

The stock map `4all` was launched directly with:

```bash
./nzportable64-sdl +map 4all
```

The engine initialized SDL audio and OpenGL, connected a local client, loaded the map, and exited normally with status `0` after the test session.

The public baseline does not redistribute the upstream archive or its contents. Redistribution must preserve the asset repository's CC BY-SA 4.0 terms and any narrower per-file notices.

## Fork policy

Do not copy upstream source into the umbrella repository.

- **Engine:** a separate FTEQW fork remains likely because NZ:P T4 requires maintained Android work that upstream does not support. First audit and attempt the pinned legacy Android path and identify the smallest required source change.
- **Gameplay:** continue using a pinned upstream QuakeC checkout. Create a separate gameplay fork only when a concrete compatibility change requires modifying gameplay, CSQC, server, or shared source.
- **Assets:** do not fork merely to obtain runtime data. Use legally distributable upstream release artifacts for local validation and preserve all applicable attribution and license information.

## Evidence classification

- Repository roles, default branches, pins, root trees, license-file paths, and build-script contents: **verified through technical research**.
- QuakeC build at the pinned revision: **experimental evidence, successful**.
- FTEQW Linux x86_64 build at the pinned revision: **experimental evidence, successful**.
- Matching PC asset archive assembly: **experimental evidence, successful**.
- Direct stock-map boot using `4all`: **experimental evidence, successful**.
- Release archive SHA-256: **not yet recorded publicly**.
- Android build and runtime status: **unverified**.
- Separate engine fork: **planned only after Android-path evidence identifies a required change**.
- Separate gameplay fork: **deferred**.
