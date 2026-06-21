from __future__ import annotations

import hashlib
import os
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

from . import __version__
from .models import Finding, FrameworkHint, InspectionResult, InventoryEntry
from .rules import classify_path, detect_framework_hints, normalize_member_path

SCHEMA_VERSION = "0.1.0"
_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class InspectionLimits:
    max_files: int = 20_000
    max_total_uncompressed: int = 4 * 1024 * 1024 * 1024
    max_file_size: int = 1024 * 1024 * 1024
    max_compression_ratio: float = 1_000.0
    max_path_length: int = 512

    def __post_init__(self) -> None:
        if self.max_files <= 0:
            raise ValueError("max_files must be positive")
        if self.max_total_uncompressed <= 0:
            raise ValueError("max_total_uncompressed must be positive")
        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        if self.max_compression_ratio <= 0:
            raise ValueError("max_compression_ratio must be positive")
        if self.max_path_length <= 0:
            raise ValueError("max_path_length must be positive")


def _sha256_stream(stream: BinaryIO, *, byte_limit: int | None = None) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    while True:
        chunk = stream.read(_CHUNK_SIZE)
        if not chunk:
            break
        count += len(chunk)
        if byte_limit is not None and count > byte_limit:
            raise ValueError("stream exceeded declared or configured byte limit")
        digest.update(chunk)
    return digest.hexdigest(), count


def _sha256_file(path: Path, *, byte_limit: int | None = None) -> tuple[str, int]:
    with path.open("rb") as handle:
        return _sha256_stream(handle, byte_limit=byte_limit)


def _build_package_fingerprint(entries: Iterable[InventoryEntry]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item.path):
        digest.update(entry.path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(entry.size).encode("ascii"))
        digest.update(b"\0")
        digest.update(entry.sha256.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _summarize(entries: list[InventoryEntry]) -> tuple[dict[str, int], dict[str, int]]:
    categories: dict[str, int] = {}
    extensions: dict[str, int] = {}
    for entry in entries:
        categories[entry.category] = categories.get(entry.category, 0) + 1
        extensions[entry.extension] = extensions.get(entry.extension, 0) + 1
    return categories, extensions


def _native_findings(entries: list[InventoryEntry]) -> list[Finding]:
    return [
        Finding(
            code="NATIVE_OR_EXECUTABLE_DEPENDENCY",
            severity="warning",
            message="Executable or native content was identified. NZ:P T4 will not execute imported code.",
            path=entry.path,
        )
        for entry in entries
        if entry.category == "native_or_executable"
    ]


def _nested_archive_findings(entries: list[InventoryEntry]) -> list[Finding]:
    return [
        Finding(
            code="NESTED_ARCHIVE_NOT_INSPECTED",
            severity="warning",
            message="Nested archives are inventoried but are not recursively opened by v0.1.0.",
            path=entry.path,
        )
        for entry in entries
        if entry.category == "archive"
    ]


def _framework_hints(entries: list[InventoryEntry]) -> list[FrameworkHint]:
    raw_hints = detect_framework_hints([entry.path for entry in entries])
    return [FrameworkHint(**hint) for hint in raw_hints]  # type: ignore[arg-type]


def _blocked_result(
    *,
    package: dict[str, object],
    findings: list[Finding],
    inventory: list[InventoryEntry] | None = None,
) -> dict[str, object]:
    entries = inventory or []
    categories, extensions = _summarize(entries)
    result = InspectionResult(
        package=package,
        inspection_complete=False,
        safe_to_process=False,
        capability_tier="U",
        inventory=entries,
        category_counts=categories,
        extension_counts=extensions,
        framework_hints=_framework_hints(entries),
        findings=findings,
    )
    return result.to_report(schema_version=SCHEMA_VERSION, inspector_version=__version__)


def _inspect_directory(path: Path, limits: InspectionLimits) -> dict[str, object]:
    findings: list[Finding] = []
    candidates: list[tuple[str, Path, int]] = []
    normalized_seen: set[str] = set()
    casefold_seen: dict[str, str] = {}
    total_size = 0

    try:
        root_resolved = path.resolve(strict=True)
    except OSError as exc:
        package = {"display_name": path.name, "type": "directory", "size": 0, "sha256": None, "fingerprint": None}
        return _blocked_result(
            package=package,
            findings=[Finding("INPUT_UNREADABLE", "error", f"Unable to resolve input directory: {exc}")],
        )

    for current_root, dir_names, file_names in os.walk(root_resolved, followlinks=False):
        current_path = Path(current_root)

        kept_dirs: list[str] = []
        for directory_name in sorted(dir_names):
            directory_path = current_path / directory_name
            relative = directory_path.relative_to(root_resolved).as_posix()
            if directory_path.is_symlink():
                findings.append(
                    Finding("SYMLINK_NOT_ALLOWED", "error", "Symbolic links are not inspected.", relative)
                )
            else:
                kept_dirs.append(directory_name)
        dir_names[:] = kept_dirs

        for file_name in sorted(file_names):
            file_path = current_path / file_name
            relative_raw = file_path.relative_to(root_resolved).as_posix()
            normalized, path_error = normalize_member_path(relative_raw, max_length=limits.max_path_length)
            if path_error or normalized is None:
                findings.append(Finding(path_error or "INVALID_PATH", "error", "Unsafe path.", relative_raw))
                continue
            if normalized in normalized_seen:
                findings.append(Finding("DUPLICATE_PATH", "error", "Duplicate normalized path.", normalized))
                continue
            folded = normalized.casefold()
            if folded in casefold_seen and casefold_seen[folded] != normalized:
                findings.append(
                    Finding(
                        "CASE_COLLISION",
                        "error",
                        f"Case-colliding path also used by {casefold_seen[folded]!r}.",
                        normalized,
                    )
                )
                continue
            normalized_seen.add(normalized)
            casefold_seen[folded] = normalized
            if file_path.is_symlink():
                findings.append(Finding("SYMLINK_NOT_ALLOWED", "error", "Symbolic links are not inspected.", normalized))
                continue
            try:
                file_stat = file_path.stat()
            except OSError as exc:
                findings.append(Finding("FILE_UNREADABLE", "error", f"Unable to stat file: {exc}", normalized))
                continue
            if not stat.S_ISREG(file_stat.st_mode):
                findings.append(Finding("NON_REGULAR_FILE", "error", "Only regular files are inspected.", normalized))
                continue
            if file_stat.st_size > limits.max_file_size:
                findings.append(
                    Finding("FILE_SIZE_LIMIT", "error", f"File exceeds {limits.max_file_size} bytes.", normalized)
                )
                continue
            candidates.append((normalized, file_path, file_stat.st_size))
            total_size += file_stat.st_size

    if len(candidates) > limits.max_files:
        findings.append(Finding("FILE_COUNT_LIMIT", "error", f"Package exceeds {limits.max_files} files."))
    if total_size > limits.max_total_uncompressed:
        findings.append(
            Finding(
                "TOTAL_SIZE_LIMIT",
                "error",
                f"Package exceeds {limits.max_total_uncompressed} uncompressed bytes.",
            )
        )

    package: dict[str, object] = {
        "display_name": path.name,
        "type": "directory",
        "size": total_size,
        "sha256": None,
        "fingerprint": None,
    }
    if any(finding.severity == "error" for finding in findings):
        return _blocked_result(package=package, findings=findings)

    inventory: list[InventoryEntry] = []
    for normalized, file_path, expected_size in sorted(candidates):
        try:
            file_hash, actual_size = _sha256_file(file_path, byte_limit=limits.max_file_size)
        except (OSError, ValueError) as exc:
            findings.append(Finding("FILE_HASH_FAILED", "error", f"Unable to hash file: {exc}", normalized))
            continue
        if actual_size != expected_size:
            findings.append(
                Finding("FILE_CHANGED_DURING_INSPECTION", "error", "File size changed during inspection.", normalized)
            )
            continue
        category, extension = classify_path(normalized)
        inventory.append(InventoryEntry(normalized, actual_size, file_hash, category, extension))

    if any(finding.severity == "error" for finding in findings):
        return _blocked_result(package=package, findings=findings, inventory=inventory)

    fingerprint = _build_package_fingerprint(inventory)
    package["sha256"] = fingerprint
    package["fingerprint"] = fingerprint
    categories, extensions = _summarize(inventory)
    findings.extend(_native_findings(inventory))
    findings.extend(_nested_archive_findings(inventory))
    result = InspectionResult(
        package=package,
        inspection_complete=True,
        safe_to_process=True,
        capability_tier="0",
        inventory=inventory,
        category_counts=categories,
        extension_counts=extensions,
        framework_hints=_framework_hints(inventory),
        findings=findings,
    )
    return result.to_report(schema_version=SCHEMA_VERSION, inspector_version=__version__)


def _zip_member_is_symlink(info: zipfile.ZipInfo) -> bool:
    unix_mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(unix_mode)


def _inspect_archive(path: Path, limits: InspectionLimits) -> dict[str, object]:
    package_hash: str | None = None
    try:
        package_hash, archive_size = _sha256_file(path)
    except OSError as exc:
        archive_size = 0
        findings = [Finding("INPUT_UNREADABLE", "error", f"Unable to read archive: {exc}")]
        package = {
            "display_name": path.name,
            "type": "iwd" if path.suffix.lower() == ".iwd" else "zip",
            "size": archive_size,
            "sha256": package_hash,
            "fingerprint": None,
        }
        return _blocked_result(package=package, findings=findings)

    archive_type = "iwd" if path.suffix.lower() == ".iwd" else "zip"
    package: dict[str, object] = {
        "display_name": path.name,
        "type": archive_type,
        "size": archive_size,
        "sha256": package_hash,
        "fingerprint": None,
    }
    findings: list[Finding] = []
    metadata: list[tuple[zipfile.ZipInfo, str]] = []
    normalized_seen: dict[str, str] = {}
    casefold_seen: dict[str, str] = {}
    total_size = 0

    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > limits.max_files:
                findings.append(Finding("FILE_COUNT_LIMIT", "error", f"Archive exceeds {limits.max_files} entries."))

            for info in infos:
                normalized, path_error = normalize_member_path(info.filename, max_length=limits.max_path_length)
                if path_error or normalized is None:
                    findings.append(
                        Finding(path_error or "INVALID_PATH", "error", "Unsafe archive member path.", info.filename)
                    )
                    continue
                if info.is_dir():
                    continue
                if _zip_member_is_symlink(info):
                    findings.append(Finding("SYMLINK_NOT_ALLOWED", "error", "Archive symlinks are rejected.", normalized))
                    continue
                if info.flag_bits & 0x1:
                    findings.append(Finding("ENCRYPTED_ENTRY", "error", "Encrypted archive entries are unsupported.", normalized))
                    continue
                if normalized in normalized_seen:
                    findings.append(
                        Finding(
                            "DUPLICATE_PATH",
                            "error",
                            f"Duplicate normalized path also used by {normalized_seen[normalized]!r}.",
                            normalized,
                        )
                    )
                    continue
                folded = normalized.casefold()
                if folded in casefold_seen and casefold_seen[folded] != normalized:
                    findings.append(
                        Finding(
                            "CASE_COLLISION",
                            "error",
                            f"Case-colliding path also used by {casefold_seen[folded]!r}.",
                            normalized,
                        )
                    )
                    continue
                normalized_seen[normalized] = info.filename
                casefold_seen[folded] = normalized

                if info.file_size > limits.max_file_size:
                    findings.append(
                        Finding("FILE_SIZE_LIMIT", "error", f"Entry exceeds {limits.max_file_size} bytes.", normalized)
                    )
                    continue
                total_size += info.file_size
                if info.file_size > 0:
                    ratio = info.file_size / max(info.compress_size, 1)
                    if ratio > limits.max_compression_ratio:
                        findings.append(
                            Finding(
                                "COMPRESSION_RATIO_LIMIT",
                                "error",
                                f"Compression ratio {ratio:.1f} exceeds {limits.max_compression_ratio:.1f}.",
                                normalized,
                            )
                        )
                        continue
                metadata.append((info, normalized))

            if total_size > limits.max_total_uncompressed:
                findings.append(
                    Finding(
                        "TOTAL_SIZE_LIMIT",
                        "error",
                        f"Archive exceeds {limits.max_total_uncompressed} uncompressed bytes.",
                    )
                )

            if any(finding.severity == "error" for finding in findings):
                return _blocked_result(package=package, findings=findings)

            inventory: list[InventoryEntry] = []
            for info, normalized in sorted(metadata, key=lambda pair: pair[1]):
                try:
                    with archive.open(info, "r") as member:
                        member_hash, actual_size = _sha256_stream(member, byte_limit=limits.max_file_size)
                except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
                    findings.append(
                        Finding("ENTRY_HASH_FAILED", "error", f"Unable to hash archive entry: {exc}", normalized)
                    )
                    continue
                if actual_size != info.file_size:
                    findings.append(
                        Finding(
                            "ENTRY_SIZE_MISMATCH",
                            "error",
                            f"Read {actual_size} bytes, expected {info.file_size}.",
                            normalized,
                        )
                    )
                    continue
                category, extension = classify_path(normalized)
                inventory.append(InventoryEntry(normalized, actual_size, member_hash, category, extension))

    except (zipfile.BadZipFile, OSError, NotImplementedError) as exc:
        findings.append(Finding("INVALID_OR_UNSUPPORTED_ARCHIVE", "error", str(exc)))
        return _blocked_result(package=package, findings=findings)

    if any(finding.severity == "error" for finding in findings):
        return _blocked_result(package=package, findings=findings, inventory=inventory)

    package["fingerprint"] = _build_package_fingerprint(inventory)
    categories, extensions = _summarize(inventory)
    findings.extend(_native_findings(inventory))
    findings.extend(_nested_archive_findings(inventory))
    result = InspectionResult(
        package=package,
        inspection_complete=True,
        safe_to_process=True,
        capability_tier="0",
        inventory=inventory,
        category_counts=categories,
        extension_counts=extensions,
        framework_hints=_framework_hints(inventory),
        findings=findings,
    )
    return result.to_report(schema_version=SCHEMA_VERSION, inspector_version=__version__)


def inspect_package(path: str | os.PathLike[str], limits: InspectionLimits | None = None) -> dict[str, object]:
    input_path = Path(path)
    selected_limits = limits or InspectionLimits()

    if input_path.is_symlink():
        package = {
            "display_name": input_path.name,
            "type": "unknown",
            "size": 0,
            "sha256": None,
            "fingerprint": None,
        }
        return _blocked_result(
            package=package,
            findings=[Finding("SYMLINK_INPUT_NOT_ALLOWED", "error", "Top-level symlink inputs are rejected.")],
        )
    if not input_path.exists():
        package = {
            "display_name": input_path.name or str(input_path),
            "type": "unknown",
            "size": 0,
            "sha256": None,
            "fingerprint": None,
        }
        return _blocked_result(
            package=package,
            findings=[Finding("INPUT_NOT_FOUND", "error", "Input path does not exist.")],
        )
    if input_path.is_dir():
        return _inspect_directory(input_path, selected_limits)
    if not input_path.is_file():
        package = {
            "display_name": input_path.name,
            "type": "unknown",
            "size": 0,
            "sha256": None,
            "fingerprint": None,
        }
        return _blocked_result(
            package=package,
            findings=[Finding("UNSUPPORTED_INPUT_TYPE", "error", "Only regular files and directories are supported.")],
        )

    suffix = input_path.suffix.lower()
    if suffix not in {".zip", ".iwd"}:
        try:
            file_hash, file_size = _sha256_file(input_path)
        except OSError as exc:
            file_hash, file_size = None, 0
            message = f"Unable to read input: {exc}"
        else:
            message = "v0.1.0 accepts only directories, ZIP archives, and ZIP-compatible IWD archives."
        package = {
            "display_name": input_path.name,
            "type": "unsupported-file",
            "size": file_size,
            "sha256": file_hash,
            "fingerprint": None,
        }
        return _blocked_result(
            package=package,
            findings=[Finding("UNSUPPORTED_INPUT_FORMAT", "error", message)],
        )
    return _inspect_archive(input_path, selected_limits)
