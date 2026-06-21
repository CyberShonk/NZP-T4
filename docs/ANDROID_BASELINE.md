# Android baseline acceptance

NZ:P T4 does not currently have a verified Android build.

## Current upstream evidence

The audited FTEQW revision contains Android-related source and build machinery, including:

- Android branches in the root `CMakeLists.txt`;
- Android SDK and NDK setup in `build_setup.sh`;
- a `--droid` path and `droid-rel` target in `build_wip.sh`;
- Android ABI and APK packaging rules in `engine/Makefile`.

This establishes that Android code exists. It does not establish that the current NZ:P fork has a usable Android build.

The same source also shows that the Android path is legacy:

- the FTEQW README marks Android unchecked and states that the upstream project is not interested in supporting Android or touch devices;
- documented NZ:P build targets omit Android;
- setup code references Android build-tools 25.0.0, SDK tools r25.2.3, `android-9` API platform files, and NDK r14b-era layouts;
- APK rules use the legacy `android update project` workflow and legacy signing commands;
- no current NZ:P Android CI job or reproducible Android build command was found.

Therefore the current classification is:

- Android-related FTEQW source: **confirmed by repository state**;
- supported upstream NZ:P Android target: **not present**;
- reproducible modern ARM64 APK: **unverified**;
- touch interface suitable for NZ:P T4: **unverified**;
- modernization effort: **planned only after desktop baseline reproduction**.

## First verified Android milestone

The first verified Android milestone requires all of the following:

- exact engine, gameplay, and asset revisions;
- reproducible ARM64 build commands from a clean checkout;
- documented Android SDK, NDK, CMake, Java, and packaging versions;
- install and launch on a defined Android device or emulator;
- boot of one native NZ:P map;
- movement, looking, firing, use, pause, death, restart, and clean exit;
- controller result and explicit touch result;
- pause/resume, surface recreation, and audio-focus observations;
- sanitized logs identifying source revisions, device, renderer, map, and exit reason.

A successful compilation or creation of an unsigned APK alone does not satisfy the milestone.

## Preconditions

Before an Android fork or modernization patch is created:

1. reproduce the pinned Linux x86_64 engine build;
2. reproduce the pinned QuakeC build;
3. assemble the pinned runtime assets;
4. boot one stock NZ:P map on desktop;
5. identify the smallest Android-specific source and build-system changes required.
