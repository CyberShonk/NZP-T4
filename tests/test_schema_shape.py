from __future__ import annotations

import json
import unittest
from pathlib import Path

from nzp_t4_inspector import inspect_package


class SchemaShapeTests(unittest.TestCase):
    def test_schema_and_report_required_keys_match(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        schema = json.loads((repository / "schemas" / "compatibility-report.schema.json").read_text(encoding="utf-8"))
        fixture = repository / "tests" / "fixtures" / "original-inspector-fixture"
        report = inspect_package(fixture)

        self.assertEqual(set(schema["required"]), set(report.keys()))
        self.assertEqual(report["schema_version"], schema["properties"]["schema_version"]["const"])
        self.assertEqual(report["inspector"]["mode"], "read-only")


if __name__ == "__main__":
    unittest.main()
