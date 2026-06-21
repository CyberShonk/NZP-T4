from __future__ import annotations

import re
from pathlib import PurePosixPath

_CATEGORY_BY_EXTENSION: dict[str, str] = {
    ".gsc": "script",
    ".csc": "script",
    ".cfg": "configuration",
    ".csv": "metadata",
    ".menu": "menu",
    ".str": "localization",
    ".ff": "fastfile",
    ".d3dbsp": "map_geometry",
    ".bsp": "map_geometry",
    ".map": "map_source",
    ".iwd": "archive",
    ".zip": "archive",
    ".7z": "archive",
    ".rar": "archive",
    ".iwi": "texture",
    ".dds": "texture",
    ".png": "texture",
    ".jpg": "texture",
    ".jpeg": "texture",
    ".tga": "texture",
    ".wav": "audio",
    ".mp3": "audio",
    ".ogg": "audio",
    ".flac": "audio",
    ".xmodel_bin": "model",
    ".xmodel_export": "model",
    ".md3": "model",
    ".mdl": "model",
    ".xanim_bin": "animation",
    ".xanim_export": "animation",
    ".exe": "native_or_executable",
    ".dll": "native_or_executable",
    ".asi": "native_or_executable",
    ".so": "native_or_executable",
    ".dylib": "native_or_executable",
    ".bat": "native_or_executable",
    ".cmd": "native_or_executable",
    ".ps1": "native_or_executable",
    ".jar": "native_or_executable",
    ".apk": "native_or_executable",
}

_FRAMEWORK_TOKENS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("T4M", re.compile(r"(?:^|[^a-z0-9])t4m(?:[^a-z0-9]|$)", re.IGNORECASE)),
    ("UGX", re.compile(r"(?:^|[^a-z0-9])ugx(?:[^a-z0-9]|$)", re.IGNORECASE)),
    ("ZCT", re.compile(r"(?:^|[^a-z0-9])zct(?:[^a-z0-9]|$)", re.IGNORECASE)),
    ("Realism-style", re.compile(r"(?:^|[^a-z0-9])realism(?:[^a-z0-9]|$)", re.IGNORECASE)),
)

_DRIVE_PATH = re.compile(r"^[A-Za-z]:")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def normalize_member_path(raw_path: str, *, max_length: int) -> tuple[str | None, str | None]:
    """Return a normalized archive path and an error code, if unsafe."""
    if not raw_path:
        return None, "EMPTY_PATH"
    if _CONTROL_CHARS.search(raw_path):
        return None, "CONTROL_CHARACTER_IN_PATH"

    portable = raw_path.replace("\\", "/")
    if portable.startswith("/") or portable.startswith("//"):
        return None, "ABSOLUTE_PATH"
    if _DRIVE_PATH.match(portable):
        return None, "DRIVE_PATH"

    parts = [part for part in portable.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        return None, "PATH_TRAVERSAL"
    if not parts:
        return None, "EMPTY_PATH"

    normalized = PurePosixPath(*parts).as_posix()
    if len(normalized) > max_length:
        return None, "PATH_TOO_LONG"
    return normalized, None


def extension_for(path: str) -> str:
    lower = path.lower()
    for compound in (".xmodel_export", ".xmodel_bin", ".xanim_export", ".xanim_bin"):
        if lower.endswith(compound):
            return compound
    suffix = PurePosixPath(lower).suffix
    return suffix


def classify_path(path: str) -> tuple[str, str]:
    extension = extension_for(path)
    return _CATEGORY_BY_EXTENSION.get(extension, "unknown"), extension or "<none>"


def detect_framework_hints(paths: list[str]) -> list[dict[str, object]]:
    hints: list[dict[str, object]] = []
    for name, pattern in _FRAMEWORK_TOKENS:
        evidence = sorted(path for path in paths if pattern.search(path))
        if evidence:
            hints.append(
                {
                    "name": name,
                    "confidence": "name-only",
                    "evidence_paths": tuple(evidence[:20]),
                    "note": "A filename/path token was found. This does not verify framework version, behavior, or compatibility.",
                }
            )
    return hints
