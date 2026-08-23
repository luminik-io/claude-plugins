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
PLUGIN_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
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


def plugin_map(manifest: dict[str, Any], path: Path) -> dict[str, dict[str, Any]]:
    plugins = manifest.get("plugins")
    require(isinstance(plugins, list), f"{path}: plugins must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(plugins):
        require(isinstance(item, dict), f"{path}: plugins[{index}] must be an object")
        name = item.get("name")
        require(
            isinstance(name, str) and PLUGIN_NAME_PATTERN.fullmatch(name) is not None,
            f"{path}: plugins[{index}].name must be kebab-case",
        )
        require(name not in result, f"{path}: duplicate plugin entry {name!r}")
        result[name] = item
    require(bool(result), f"{path}: at least one plugin is required")
    return result


def require_matching_plugin_sets(
    claude_plugins: dict[str, dict[str, Any]],
    codex_plugins: dict[str, dict[str, Any]],
) -> None:
    require(
        claude_plugins.keys() == codex_plugins.keys(),
        f"marketplace plugin sets differ: Claude={sorted(claude_plugins)} "
        f"Codex={sorted(codex_plugins)}",
    )


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

    claude_plugins = plugin_map(claude, claude_path)
    codex_plugins = plugin_map(codex, codex_path)
    require_matching_plugin_sets(claude_plugins, codex_plugins)

    submodule_lines = git_output(
        root, "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"
    ).splitlines()
    submodule_paths = {
        line.split(maxsplit=1)[1]
        for line in submodule_lines
        if len(line.split(maxsplit=1)) == 2
    }
    expected_submodule_paths = {f"plugins/{name}" for name in claude_plugins}
    require(
        submodule_paths == expected_submodule_paths,
        f".gitmodules plugin paths differ: declared={sorted(expected_submodule_paths)} "
        f"configured={sorted(submodule_paths)}",
    )

    plugin_versions: set[str] = set()
    for plugin_name, claude_entry in claude_plugins.items():
        codex_entry = codex_plugins[plugin_name]
        plugin_root = root / "plugins" / plugin_name
        require(
            claude_entry.get("source") == f"./plugins/{plugin_name}",
            f"{claude_path}: {plugin_name} source must be its pinned submodule path",
        )

        source = codex_entry.get("source")
        require(
            isinstance(source, dict),
            f"{codex_path}: {plugin_name} source must be an object",
        )
        require(
            source.get("source") == "url",
            f"{codex_path}: {plugin_name} source must be URL-backed",
        )
        expected_repository = git_output(
            root,
            "config",
            "-f",
            ".gitmodules",
            "--get",
            f"submodule.plugins/{plugin_name}.url",
        )
        require(
            source.get("url") == expected_repository,
            f"{codex_path}: {plugin_name} source URL differs from .gitmodules",
        )
        source_ref = source.get("ref")
        require(
            isinstance(source_ref, str)
            and SHA_PATTERN.fullmatch(source_ref) is not None,
            f"{codex_path}: {plugin_name} source ref must be an exact 40-character commit SHA",
        )

        policy = codex_entry.get("policy")
        require(
            isinstance(policy, dict),
            f"{codex_path}: {plugin_name} policy must be an object",
        )
        require(
            policy.get("installation")
            in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"},
            f"{codex_path}: {plugin_name} has invalid policy.installation",
        )
        require(
            policy.get("authentication") in {"ON_INSTALL", "ON_USE"},
            f"{codex_path}: {plugin_name} has invalid policy.authentication",
        )
        require(
            isinstance(codex_entry.get("category"), str)
            and bool(codex_entry["category"].strip()),
            f"{codex_path}: {plugin_name} category is required",
        )

        require(plugin_root.is_dir(), f"{plugin_root}: submodule is not initialized")
        plugin_head = git_output(plugin_root, "rev-parse", "HEAD")
        require(
            source_ref == plugin_head,
            f"{codex_path}: {plugin_name} source ref {source_ref} does not match "
            f"submodule HEAD {plugin_head}",
        )
        staged_gitlink = git_output(
            root, "ls-files", "--stage", f"plugins/{plugin_name}"
        ).split()
        require(
            len(staged_gitlink) >= 2 and staged_gitlink[0] == "160000",
            f"{plugin_root}: expected a staged gitlink",
        )
        require(
            staged_gitlink[1] == plugin_head,
            f"{plugin_root}: gitlink {staged_gitlink[1]} does not match "
            f"checked-out HEAD {plugin_head}",
        )

        claude_plugin_path = plugin_root / ".claude-plugin" / "plugin.json"
        codex_plugin_path = plugin_root / ".codex-plugin" / "plugin.json"
        claude_plugin = load_json(claude_plugin_path)
        codex_plugin = load_json(codex_plugin_path)
        for path, manifest in (
            (claude_plugin_path, claude_plugin),
            (codex_plugin_path, codex_plugin),
        ):
            require(
                manifest.get("name") == plugin_name,
                f"{path}: name must be {plugin_name!r}",
            )
            require(
                manifest.get("version") == claude_entry.get("version"),
                f"{path}: version must match the Claude marketplace entry",
            )
        require(
            claude_plugin.get("version") == codex_plugin.get("version"),
            f"{plugin_name}: Claude and Codex plugin versions differ",
        )
        plugin_version = claude_plugin.get("version")
        require(
            isinstance(plugin_version, str) and bool(plugin_version),
            f"{claude_plugin_path}: version is required",
        )
        plugin_versions.add(plugin_version)

        skill_files = sorted((plugin_root / "skills").glob("*/SKILL.md"))
        require(bool(skill_files), f"{plugin_root}: at least one skill is required")
        for skill_file in skill_files:
            require(
                (skill_file.parent / "agents" / "openai.yaml").is_file(),
                f"{skill_file.parent}: agents/openai.yaml is missing",
            )

    metadata = claude.get("metadata")
    require(isinstance(metadata, dict), f"{claude_path}: metadata must be an object")
    if len(plugin_versions) == 1:
        require(
            metadata.get("version") == next(iter(plugin_versions)),
            f"{claude_path}: metadata.version must match the plugin version",
        )

    readme = (root / "README.md").read_text(encoding="utf-8")
    commands = [
        "claude plugin marketplace add luminik-io/claude-plugins",
        "codex plugin marketplace add luminik-io/claude-plugins",
    ]
    for plugin_name in claude_plugins:
        commands.extend(
            (
                f"claude plugin install {plugin_name}@{EXPECTED_NAME}",
                f"codex plugin add {plugin_name}@{EXPECTED_NAME}",
            )
        )
    for command in commands:
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
