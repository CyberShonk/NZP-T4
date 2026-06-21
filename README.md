# NZ:P T4

NZ:P T4 is an **Android-first compatibility project** built around Nazi Zombies: Portable. Its long-term purpose is to investigate and progressively support legally obtained Call of Duty: World at War custom Zombies maps without redistributing proprietary game data or third-party maps.

This repository is an early public foundation. It does **not** currently provide an Android game build or claim that any World at War custom map is playable.

## Current capability

The first implemented component is a read-only package inspector. It can inspect:

- directories;
- ZIP archives;
- ZIP-compatible IWD archives.

It generates a structured compatibility report containing package hashes, normalized file inventory, format counts, safety findings, possible native-code dependencies, and conservative framework-name hints. It does not execute, install, or extract imported content.

## Non-goals

NZ:P T4 is not:

- a World at War decompiler;
- a generic map-conversion service;
- a source or asset redistribution project;
- a promise of universal map compatibility;
- a replacement for obtaining maps and game files from authorized sources.

## Inspector quick start

Requires Python 3.11 or newer.

```bash
python -m pip install -e .
nzp-t4-inspect /path/to/package --output compatibility_report.json --pretty
```

Or run directly from the repository:

```bash
PYTHONPATH=src python -m nzp_t4_inspector /path/to/package --pretty
```

Exit codes:

- `0`: inspection completed without blocking safety findings;
- `2`: a report was produced, but the package was blocked by safety or format findings;
- `1`: command usage or unexpected internal failure.

## Validation

```bash
./tools/check-project.sh
```

## Repository status

See [CURRENT_STATUS.md](CURRENT_STATUS.md). Project work must follow [PROJECT_PROCESS.md](PROJECT_PROCESS.md).

## Content policy

Do not submit or commit proprietary game files, third-party custom maps, extracted assets, native framework binaries, signing material, or private research. See [docs/CONTENT_POLICY.md](docs/CONTENT_POLICY.md).

## Upstream relationship

NZ:P T4 is an independent, unofficial project. It is not endorsed by Activision, Treyarch, or the NZ:P team. Nazi Zombies: Portable and its source components are maintained separately by the NZ:P team. See [docs/UPSTREAM.md](docs/UPSTREAM.md).

## License

Original source in this repository is licensed under the GNU General Public License version 2 only. Third-party components retain their own notices and licenses. No upstream engine, NZ:P asset package, World at War content, or third-party map is included in this foundation.
