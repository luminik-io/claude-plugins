#!/usr/bin/env python3
"""Fail closed when the Claude and Codex marketplace views drift."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_NAME = "luminik-plugins"
EXPECTED_PLUGIN = "event-outbound"
EXPECTED_REPOSITORY = "https://github.com/luminik-io/event-outbound-skill.git"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class VerificationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise VerificationError(f"{path}: duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{path}: root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def one_plugin(manifest: dict[str, Any], path: Path) -> dict[str, Any]:
    plugins = manifest.get("plugins")
    require(isinstance(plugins, list), f"{path}: plugins must be an array")
    matches = [
        item
        for item in plugins
        if isinstance(item, dict) and item.get("name") == EXPECTED_PLUGIN
    ]
    require(
        len(matches) == 1, f"{path}: expected exactly one {EXPECTED_PLUGIN!r} entry"
    )
    return matches[0]


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def verify(root: Path) -> None:
    claude_path = root / ".claude-plugin" / "marketplace.json"
    codex_path = root / ".agents" / "plugins" / "marketplace.json"
    plugin_root = root / "plugins" / EXPECTED_PLUGIN

    claude = load_json(claude_path)
    codex = load_json(codex_path)
    require(
        claude.get("name") == EXPECTED_NAME,
        f"{claude_path}: unexpected marketplace name",
    )
    require(
        codex.get("name") == EXPECTED_NAME, f"{codex_path}: unexpected marketplace name"
    )
    interface = codex.get("interface")
    require(
        isinstance(interface, dict) and isinstance(interface.get("displayName"), str),
        f"{codex_path}: interface.displayName is required",
    )

    claude_entry = one_plugin(claude, claude_path)
    codex_entry = one_plugin(codex, codex_path)
    require(
        claude_entry.get("source") == f"./plugins/{EXPECTED_PLUGIN}",
        f"{claude_path}: Claude source must remain the pinned submodule path",
    )

    source = codex_entry.get("source")
    require(isinstance(source, dict), f"{codex_path}: source must be an object")
    require(
        source.get("source") == "url", f"{codex_path}: Codex source must be URL-backed"
    )
    require(
        source.get("url") == EXPECTED_REPOSITORY,
        f"{codex_path}: unexpected Codex source URL",
    )
    source_ref = source.get("ref")
    require(
        isinstance(source_ref, str) and SHA_PATTERN.fullmatch(source_ref) is not None,
        f"{codex_path}: Codex source ref must be an exact 40-character commit SHA",
    )

    policy = codex_entry.get("policy")
    require(isinstance(policy, dict), f"{codex_path}: policy must be an object")
    require(
        policy.get("installation")
        in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"},
        f"{codex_path}: invalid policy.installation",
    )
    require(
        policy.get("authentication") in {"ON_INSTALL", "ON_USE"},
        f"{codex_path}: invalid policy.authentication",
    )
    require(
        isinstance(codex_entry.get("category"), str)
        and bool(codex_entry["category"].strip()),
        f"{codex_path}: category is required",
    )

    require(plugin_root.is_dir(), f"{plugin_root}: submodule is not initialized")
    plugin_head = git_output(plugin_root, "rev-parse", "HEAD")
    require(
        source_ref == plugin_head,
        f"{codex_path}: source ref {source_ref} does not match submodule HEAD {plugin_head}",
    )
    staged_gitlink = git_output(
        root, "ls-files", "--stage", f"plugins/{EXPECTED_PLUGIN}"
    ).split()
    require(
        len(staged_gitlink) >= 2 and staged_gitlink[0] == "160000",
        f"{plugin_root}: expected a staged gitlink",
    )
    require(
        staged_gitlink[1] == plugin_head,
        f"{plugin_root}: gitlink {staged_gitlink[1]} does not match checked-out HEAD {plugin_head}",
    )

    claude_plugin = load_json(plugin_root / ".claude-plugin" / "plugin.json")
    codex_plugin = load_json(plugin_root / ".codex-plugin" / "plugin.json")
    for path, manifest in (
        (plugin_root / ".claude-plugin" / "plugin.json", claude_plugin),
        (plugin_root / ".codex-plugin" / "plugin.json", codex_plugin),
    ):
        require(
            manifest.get("name") == EXPECTED_PLUGIN,
            f"{path}: name must be {EXPECTED_PLUGIN!r}",
        )
        require(
            manifest.get("version") == claude_entry.get("version"),
            f"{path}: version must match the Claude marketplace entry",
        )
    require(
        claude_plugin.get("version") == codex_plugin.get("version"),
        "Claude and Codex plugin versions differ",
    )
    metadata = claude.get("metadata")
    require(
        isinstance(metadata, dict)
        and metadata.get("version") == claude_plugin.get("version"),
        f"{claude_path}: metadata.version must match the plugin version",
    )

    skill_root = plugin_root / "skills" / EXPECTED_PLUGIN
    require((skill_root / "SKILL.md").is_file(), f"{skill_root}: SKILL.md is missing")
    require(
        (skill_root / "agents" / "openai.yaml").is_file(),
        f"{skill_root}: agents/openai.yaml is missing",
    )

    gitmodules = (root / ".gitmodules").read_text(encoding="utf-8")
    require(
        EXPECTED_REPOSITORY in gitmodules, ".gitmodules and Codex source URL differ"
    )

    readme = (root / "README.md").read_text(encoding="utf-8")
    for command in (
        "claude plugin marketplace add luminik-io/claude-plugins",
        "claude plugin install event-outbound@luminik-plugins",
        "codex plugin marketplace add luminik-io/claude-plugins",
        "codex plugin add event-outbound@luminik-plugins",
    ):
        require(command in readme, f"README.md: missing install command {command!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    try:
        verify(args.root.resolve())
    except (VerificationError, subprocess.CalledProcessError) as exc:
        print(f"marketplace verification failed: {exc}", file=sys.stderr)
        return 1
    print("Claude and Codex marketplace manifests are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
