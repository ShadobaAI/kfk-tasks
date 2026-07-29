from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from memory_bank_mcp.store import MemoryBankStore
from memory_bank_mcp.validator import MemoryBankValidator


class ValidatorTests(unittest.TestCase):
    def test_reports_structure_link_anchor_id_and_portability_problems(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                """---
title: Index
type: index
status: verified
updated: 2026-07-29
sources:
  - "repo:kafka-adapter:README.md"
---
# Index
## Summary
- Summary.
## Duplicate
## Duplicate
[Missing](missing.md)
[Bad anchor](README.md#no-such-anchor)
Machine path C:\\temp\\value.
""",
                encoding="utf-8",
            )
            (root / "spec-a.md").write_text(
                """---
title: Spec
id: SPEC-0001
type: specification
status: unknown
updated: 2026-07-29
---
# Spec
## Summary
- Summary.
""",
                encoding="utf-8",
            )
            result = MemoryBankValidator(MemoryBankStore(root)).run()
            codes = {issue["code"] for issue in result["issues"]}
            self.assertTrue(
                {"duplicate-heading", "broken-link", "broken-anchor", "machine-path", "invalid-status"}.issubset(codes)
            )


if __name__ == "__main__":
    unittest.main()

