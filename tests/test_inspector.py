from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

from nzp_t4_inspector import InspectionLimits, inspect_package


class InspectorTests(unittest.TestCase):
    def test_original_directory_fixture_is_deterministic(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "original-inspector-fixture"
        first = inspect_package(fixture)
        second = inspect_package(fixture)

        self.assertTrue(first["safe_to_process"])
        self.assertEqual(first["capability_tier"], "0")
        self.assertEqual(first["package"]["fingerprint"], second["package"]["fingerprint"])
        self.assertEqual(first["summary"]["file_count"], 3)
        self.assertEqual(first["summary"]["category_counts"]["script"], 1)

    def test_safe_zip_is_inventoried(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "sample.zip"
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("scripts/test.gsc", "main() {}")
                archive.writestr("metadata/info.csv", "key,value\n")

            report = inspect_package(archive_path)
            self.assertTrue(report["inspection_complete"])
            self.assertTrue(report["safe_to_process"])
            self.assertEqual(report["package"]["type"], "zip")
            self.assertEqual(report["summary"]["file_count"], 2)

    def test_iwd_uses_zip_reader(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "sample.iwd"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("maps/example.gsc", "main() {}")

            report = inspect_package(archive_path)
            self.assertTrue(report["safe_to_process"])
            self.assertEqual(report["package"]["type"], "iwd")

    def test_path_traversal_is_rejected_before_entry_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "traversal.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../outside.txt", "blocked")

            report = inspect_package(archive_path)
            self.assertFalse(report["safe_to_process"])
            self.assertEqual(report["capability_tier"], "U")
            self.assertIn("PATH_TRAVERSAL", {item["code"] for item in report["findings"]})

    def test_windows_drive_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "drive.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("C:\\outside.txt", "blocked")

            report = inspect_package(archive_path)
            self.assertFalse(report["safe_to_process"])
            self.assertIn("DRIVE_PATH", {item["code"] for item in report["findings"]})

    def test_archive_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "symlink.zip"
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(info, "target")

            report = inspect_package(archive_path)
            self.assertFalse(report["safe_to_process"])
            self.assertIn("SYMLINK_NOT_ALLOWED", {item["code"] for item in report["findings"]})

    def test_case_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "collision.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("Scripts/Test.gsc", "one")
                archive.writestr("scripts/test.gsc", "two")

            report = inspect_package(archive_path)
            self.assertFalse(report["safe_to_process"])
            self.assertIn("CASE_COLLISION", {item["code"] for item in report["findings"]})

    def test_compression_ratio_limit_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "ratio.zip"
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("large.txt", "A" * 100_000)

            report = inspect_package(archive_path, InspectionLimits(max_compression_ratio=2.0))
            self.assertFalse(report["safe_to_process"])
            self.assertIn("COMPRESSION_RATIO_LIMIT", {item["code"] for item in report["findings"]})

    def test_native_dependency_and_name_hint_are_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "hints.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("mods/t4m/helper.dll", b"synthetic-test-bytes")

            report = inspect_package(archive_path)
            self.assertTrue(report["safe_to_process"])
            self.assertIn("NATIVE_OR_EXECUTABLE_DEPENDENCY", {item["code"] for item in report["findings"]})
            self.assertIn("T4M", {item["name"] for item in report["framework_hints"]})

    def test_unsupported_file_still_produces_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "sample.bin"
            input_path.write_bytes(b"data")

            report = inspect_package(input_path)
            self.assertFalse(report["safe_to_process"])
            self.assertEqual(report["package"]["type"], "unsupported-file")
            self.assertRegex(report["package"]["sha256"], r"^[a-f0-9]{64}$")


    def test_missing_input_report_has_complete_package_shape(self) -> None:
        report = inspect_package("/definitely/not/a/real/nzp-t4-input")
        self.assertFalse(report["safe_to_process"])
        self.assertEqual(
            set(report["package"]),
            {"display_name", "type", "size", "sha256", "fingerprint"},
        )

    def test_directory_case_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "fixture"
            (root / "Scripts").mkdir(parents=True)
            (root / "scripts").mkdir(parents=True)
            (root / "Scripts" / "Test.gsc").write_text("one", encoding="utf-8")
            (root / "scripts" / "test.gsc").write_text("two", encoding="utf-8")

            report = inspect_package(root)
            self.assertFalse(report["safe_to_process"])
            self.assertIn("CASE_COLLISION", {item["code"] for item in report["findings"]})

    def test_nested_archive_is_reported_but_not_opened(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "fixture"
            root.mkdir()
            (root / "nested.iwd").write_bytes(b"not opened")

            report = inspect_package(root)
            self.assertTrue(report["safe_to_process"])
            self.assertIn("NESTED_ARCHIVE_NOT_INSPECTED", {item["code"] for item in report["findings"]})

    def test_report_is_json_serializable(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "original-inspector-fixture"
        report = inspect_package(fixture)
        rendered = json.dumps(report, sort_keys=True)
        self.assertIn('"schema_version": "0.1.0"', rendered)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_directory_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "fixture"
            root.mkdir()
            (root / "file.txt").write_text("data", encoding="utf-8")
            try:
                (root / "link.txt").symlink_to(root / "file.txt")
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            report = inspect_package(root)
            self.assertFalse(report["safe_to_process"])
            self.assertIn("SYMLINK_NOT_ALLOWED", {item["code"] for item in report["findings"]})


if __name__ == "__main__":
    unittest.main()
