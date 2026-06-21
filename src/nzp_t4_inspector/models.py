from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class InventoryEntry:
    path: str
    size: int
    sha256: str
    category: str
    extension: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FrameworkHint:
    name: str
    confidence: str
    evidence_paths: tuple[str, ...]
    note: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_paths"] = list(self.evidence_paths)
        return data


@dataclass
class InspectionResult:
    package: dict[str, Any]
    inspection_complete: bool
    safe_to_process: bool
    capability_tier: str
    inventory: list[InventoryEntry] = field(default_factory=list)
    category_counts: dict[str, int] = field(default_factory=dict)
    extension_counts: dict[str, int] = field(default_factory=dict)
    framework_hints: list[FrameworkHint] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def to_report(self, *, schema_version: str, inspector_version: str) -> dict[str, Any]:
        return {
            "schema_version": schema_version,
            "inspector": {
                "name": "nzp-t4-inspector",
                "version": inspector_version,
                "mode": "read-only",
            },
            "package": self.package,
            "inspection_complete": self.inspection_complete,
            "safe_to_process": self.safe_to_process,
            "capability_tier": self.capability_tier,
            "inventory": [entry.to_dict() for entry in self.inventory],
            "summary": {
                "file_count": len(self.inventory),
                "total_uncompressed_size": sum(entry.size for entry in self.inventory),
                "category_counts": dict(sorted(self.category_counts.items())),
                "extension_counts": dict(sorted(self.extension_counts.items())),
            },
            "framework_hints": [hint.to_dict() for hint in self.framework_hints],
            "findings": [finding.to_dict() for finding in self.findings],
        }
