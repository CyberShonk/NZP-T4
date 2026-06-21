# Linux desktop baseline

Status: **verified on 2026-06-21**

This document records the first reproduced Linux x86_64 NZ:P baseline used by NZ:P T4. It proves that the audited engine, gameplay, and asset revisions can form a working desktop runtime when the matching compiled PC asset archive is used.

It does not establish:

- a supported desktop release produced by NZ:P T4;
- an Android build;
- ARM64 Android execution;
- World at War map loading;
- FastFile, D3DBSP, or GSC compatibility.

## Component revisions

| Component | Revision |
|---|---|
| Assets | `5c3527c0e60381db3afb2489bc882a44b76b9daf` |
| FTEQW | `f68a2b547d2dc4bf6886b922baa1bff487cc5038` |
| QuakeC | `6613eb72359d1244e6034d31c3d07f78c1cf9b6f` |

The `newest` asset release tag resolved to the exact pinned asset revision during the test.

## Build environment

The successful engine build ran inside a Fedora 42 Toolbox on a Bazzite host. The build used native GNU/Linux x86_64 tools and development headers for SDL2, OpenGL, XCB, X11, audio, image, compression, Vorbis, Opus, and FreeType support.

The FTEQW checkout used a physical path without whitespace. A prior build under a path containing `Active projects` failed because an upstream dependency build truncated an absolute include path.

QuakeC used an isolated Python 3.12 environment. The pinned dependency set was not compatible with the host's Python 3.14.

## QuakeC reproduction

Create an isolated Python 3.12 environment and install the resolved dependencies:

```bash
uv python install 3.12
uv venv --python 3.12 "$WORK/quakec-venv"
uv pip install \
  --python "$WORK/quakec-venv/bin/python" \
  colorama==0.4.6 \
  fastcrc==0.3.0 \
  pandas==2.1.4
```

Build the pinned checkout:

```bash
git -C "$WORK/quakec" checkout --detach \
  6613eb72359d1244e6034d31c3d07f78c1cf9b6f

cd "$WORK/quakec"
./tools/qc-compiler-gnu.sh
```

Successful FTE outputs:

| Output | SHA-256 |
|---|---|
| `build/fte/csprogs.dat` | `740097be8470c3d90c028dab963d797e1b8af296537d3ba5dd53256baefbb543` |
| `build/fte/csprogs.lno` | `42d6a62abc67b1eb67466551aa0cfaed3dd00b6756a832bed41d78a8ad32fd3d` |
| `build/fte/menu.dat` | `360701578139138a43e3beb3066215a737d30f94b9a95032936b30089e4c16d4` |
| `build/fte/qwprogs.dat` | `93c97b487c42a6611b611119b794eb1ac64ce6bae07855e542c84205a25b7a33` |

## FTEQW reproduction

The Fedora development environment requested these packages:

```text
gcc gcc-c++ make cmake pkgconf-pkg-config SDL2-devel
mesa-libGL-devel libglvnd-devel libxcb-devel libX11-devel
libXext-devel libXcursor-devel libXi-devel libXrandr-devel
libXinerama-devel alsa-lib-devel pulseaudio-libs-devel
libjpeg-turbo-devel libpng-devel zlib-devel libvorbis-devel
opus-devel freetype-devel curl wget zip unzip patch
```

Build the pinned checkout from a whitespace-free path:

```bash
git -C "$WORK/fteqw" checkout --detach \
  f68a2b547d2dc4bf6886b922baa1bff487cc5038

cd "$WORK/fteqw/engine"
export CC=gcc
export CXX=g++
export STRIP=strip
export PKG_CONFIG=pkg-config

make makelibs FTE_TARGET=SDL2
make m-rel \
  FTE_TARGET=SDL2 \
  FTE_CONFIG=nzportable \
  -j"$(nproc)"
```

Successful outputs:

```text
release/nzportable-sdl2
release/nzportable-sdl2.db
```

The stripped engine executable had SHA-256:

```text
567de5a44aed4ee285a172879498a8c41c7675e6cd4d428ffa456d205081948f
```

`ldd` reported no unresolved libraries.

## Runtime assembly

Copying only `assets/pc` and `assets/common` from the source checkout did not produce a playable runtime because compiled BSP files were absent.

Use the matching official `pc-nzp-assets.zip` release archive, then add the reproduced gameplay and engine outputs:

```bash
mkdir -p "$RUNTIME"
unzip -q pc-nzp-assets.zip -d "$RUNTIME"

cp -a "$WORK/quakec/build/fte/." "$RUNTIME/nzp/"
install -m 0755 \
  "$WORK/fteqw/engine/release/nzportable-sdl2" \
  "$RUNTIME/nzportable64-sdl"
```

The matching archive contained 19 compiled BSP maps. The archive SHA-256 still needs to be added to public documentation before treating the release artifact itself as immutably identified.

## Runtime test

The stock map was launched directly:

```bash
cd "$RUNTIME"
./nzportable64-sdl +map 4all
```

Observed successful indicators:

```text
OpenGL renderer initialized
------- Nazi Zombies Portable Initialized -------
client Unknown Soldier connected
```

The test ended with:

```text
Unknown Soldier has left the game.
Runtime exit status: 0
```

This establishes a successful direct stock-map boot. Menu-based map selection was not separately re-verified after the asset assembly was corrected.

## Non-blocking runtime warnings

The successful session emitted:

```text
PF_fclose: File out of range (-1)
WARNING: SV_StartSound: sound demon/dland2.wav not precached
```

These warnings did not prevent the local client from connecting or the map from running.

First-launch messages for absent `config.cfg`, `user_settings.cfg`, and `autoexec.cfg` were also observed and did not block startup.

## Failed attempts and resolved causes

1. **Python 3.14 dependency failure**
   - `pandas==2.1.4` and its NumPy dependency did not install successfully.
   - Resolved by using an isolated Python 3.12 environment.

2. **Whitespace in the FTEQW checkout path**
   - The dependency build truncated an Ogg include path and failed to find `ogg/ogg.h`.
   - Resolved by using a physical checkout path without spaces.

3. **Missing development headers**
   - The engine build initially lacked SDL2, OpenGL, and XCB development files.
   - Resolved by building inside a Fedora 42 Toolbox with the required development packages.

4. **Incomplete source-only asset assembly**
   - The engine initialized, but menu-selected maps returned to the menu because BSP files were absent.
   - Resolved by using the matching official PC asset release archive.

## Evidence classification

- QuakeC build: **experimental evidence, successful**.
- FTEQW Linux x86_64 build: **experimental evidence, successful**.
- Matching PC runtime assembly: **experimental evidence, successful**.
- Direct stock-map boot: **experimental evidence, successful**.
- Android build: **unverified**.
- World at War compatibility: **unverified**.
