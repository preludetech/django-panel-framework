"""The release tag, the project version and the newest changelog entry must agree."""

from __future__ import annotations

import pytest

from tests.check_release_tag import release_mismatches

# The session-wide stub-table fixture needs a test database, and pytest-django
# only builds one when a collected test asks for it. Without this mark, running
# this module on its own errors in that fixture.
pytestmark = pytest.mark.django_db


def _pyproject(version: str) -> str:
    return f'[project]\nname = "django-panel-framework"\nversion = "{version}"\n'


def _changelog(version: str | None) -> str:
    if version is None:
        return "# Changelog\n\nNothing released yet.\n"
    return f"# Changelog\n\n## [{version}] - 2026-11-27\n\nFirst release.\n"


@pytest.mark.parametrize(
    ("tag", "version", "changelog_version", "expected"),
    [
        ("v0.1.0", "0.1.0", "0.1.0", []),
        (
            "v0.2.0",
            "0.1.0",
            "0.2.0",
            ["pyproject.toml version 0.1.0 is not tag v0.2.0"],
        ),
        (
            "v0.2.0",
            "0.2.0",
            "0.1.0",
            ["newest CHANGELOG.md entry 0.1.0 is not tag v0.2.0"],
        ),
        (
            "v0.2.0",
            "0.1.0",
            "0.1.0",
            [
                "pyproject.toml version 0.1.0 is not tag v0.2.0",
                "newest CHANGELOG.md entry 0.1.0 is not tag v0.2.0",
            ],
        ),
        (
            "v0.1.0",
            "0.1.0",
            None,
            ["newest CHANGELOG.md entry None is not tag v0.1.0"],
        ),
    ],
    ids=[
        "all_agree",
        "tag_differs",
        "version_differs",
        "changelog_and_version_differ",
        "changelog_has_no_entry",
    ],
)
def test_release_mismatches(
    tag: str, version: str, changelog_version: str | None, expected: list[str]
) -> None:
    assert (
        release_mismatches(tag, _pyproject(version), _changelog(changelog_version))
        == expected
    )
