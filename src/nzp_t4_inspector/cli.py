from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .inspector import InspectionLimits, inspect_package


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nzp-t4-inspect",
        description="Read-only inventory and safety inspection for a directory, ZIP, or IWD package.",
    )
    parser.add_argument("input", help="Path to a directory, ZIP archive, or ZIP-compatible IWD archive")
    parser.add_argument("-o", "--output", type=Path, help="Write JSON report to this path instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Indent JSON output")
    parser.add_argument("--max-files", type=_positive_int, default=20_000)
    parser.add_argument("--max-total-bytes", type=_positive_int, default=4 * 1024 * 1024 * 1024)
    parser.add_argument("--max-file-bytes", type=_positive_int, default=1024 * 1024 * 1024)
    parser.add_argument("--max-compression-ratio", type=_positive_float, default=1_000.0)
    parser.add_argument("--max-path-length", type=_positive_int, default=512)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    limits = InspectionLimits(
        max_files=args.max_files,
        max_total_uncompressed=args.max_total_bytes,
        max_file_size=args.max_file_bytes,
        max_compression_ratio=args.max_compression_ratio,
        max_path_length=args.max_path_length,
    )
    try:
        report = inspect_package(args.input, limits)
        rendered = json.dumps(
            report,
            indent=2 if args.pretty else None,
            sort_keys=args.pretty,
            ensure_ascii=False,
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
    except (OSError, ValueError) as exc:
        print(f"nzp-t4-inspect: {exc}", file=sys.stderr)
        return 1

    return 0 if report.get("safe_to_process") is True else 2
