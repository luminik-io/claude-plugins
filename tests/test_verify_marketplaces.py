from __future__ import annotations

import unittest
from pathlib import Path

from scripts.verify_marketplaces import (
    VerificationError,
    plugin_map,
    require_matching_plugin_sets,
)


class MarketplaceSetTests(unittest.TestCase):
    def test_rejects_plugin_declared_only_for_claude(self) -> None:
        claude = plugin_map(
            {"plugins": [{"name": "event-outbound"}, {"name": "future-plugin"}]},
            Path("claude.json"),
        )
        codex = plugin_map(
            {"plugins": [{"name": "event-outbound"}]}, Path("codex.json")
        )

        with self.assertRaisesRegex(VerificationError, "plugin sets differ"):
            require_matching_plugin_sets(claude, codex)

    def test_rejects_plugin_declared_only_for_codex(self) -> None:
        claude = plugin_map(
            {"plugins": [{"name": "event-outbound"}]}, Path("claude.json")
        )
        codex = plugin_map(
            {"plugins": [{"name": "event-outbound"}, {"name": "future-plugin"}]},
            Path("codex.json"),
        )

        with self.assertRaisesRegex(VerificationError, "plugin sets differ"):
            require_matching_plugin_sets(claude, codex)

    def test_accepts_identical_plugin_sets_in_different_orders(self) -> None:
        claude = plugin_map(
            {"plugins": [{"name": "event-outbound"}, {"name": "future-plugin"}]},
            Path("claude.json"),
        )
        codex = plugin_map(
            {"plugins": [{"name": "future-plugin"}, {"name": "event-outbound"}]},
            Path("codex.json"),
        )

        require_matching_plugin_sets(claude, codex)

    def test_rejects_duplicate_plugin_names(self) -> None:
        with self.assertRaisesRegex(VerificationError, "duplicate plugin entry"):
            plugin_map(
                {"plugins": [{"name": "event-outbound"}, {"name": "event-outbound"}]},
                Path("claude.json"),
            )


if __name__ == "__main__":
    unittest.main()
