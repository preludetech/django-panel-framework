"""Fail a release when the tag, the project version and the changelog disagree.

Run from the repository root: `python -m tests.check_release_tag <tag>`.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


def release_mismatches(tag: str, pyproject_text: str, changelog_text: str) -> list[str]:
    """Each way the tag, the project version and the newest changelog entry disagree."""
    version = tomllib.loads(pyproject_text)["project"]["version"]
    newest = re.search(r"^## \[([^\]]+)\]", changelog_text, re.MULTILINE)
    changelog_version = newest.group(1) if newest else None
    tagged = tag.removeprefix("v")
    mismatches: list[str] = []
    if version != tagged:
        mismatches.append(f"pyproject.toml version {version} is not tag {tag}")
    if changelog_version != tagged:
        mismatches.append(
            f"newest CHANGELOG.md entry {changelog_version} is not tag {tag}"
        )
    return mismatches


def main(argv: list[str]) -> int:
    mismatches = release_mismatches(
        argv[1], Path("pyproject.toml").read_text(), Path("CHANGELOG.md").read_text()
    )
    print("\n".join(mismatches))  # noqa: T201
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
