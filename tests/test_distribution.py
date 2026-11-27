"""The built wheel and sdist hold the right files and the right metadata."""

from __future__ import annotations

import os
import subprocess
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# The session-wide stub-table fixture needs a test database, and pytest-django
# only builds one when a collected test asks for it. Without this mark, running
# this module on its own errors in that fixture.
pytestmark = pytest.mark.django_db


@pytest.fixture(scope="module")
def build_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    # With no flag, `uv build` builds the sdist, then the wheel from that sdist.
    # The build backend comes from the dev group, so no download is needed.
    subprocess.run(  # noqa: S603
        ["uv", "build", "--no-build-isolation", "--out-dir", str(out)],  # noqa: S607
        cwd=REPO_ROOT,
        check=True,
    )
    return out


@pytest.fixture(scope="module")
def wheel(build_dir: Path) -> Path:
    given = os.environ.get("PANEL_FRAMEWORK_WHEEL")
    if given:
        return Path(given)
    return next(build_dir.glob("*.whl"))


@pytest.fixture(scope="module")
def sdist(build_dir: Path) -> Path:
    return next(build_dir.glob("*.tar.gz"))


@pytest.fixture(scope="module")
def wheel_names(wheel: Path) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        return archive.namelist()


def _tracked_package_files() -> list[str]:
    listing = subprocess.run(
        ["git", "ls-files", "panel_framework"],  # noqa: S607
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return listing.stdout.splitlines()


def test_wheel_holds_every_tracked_package_file(wheel_names: list[str]) -> None:
    missing = set(_tracked_package_files()) - set(wheel_names)

    assert missing == set()


@pytest.mark.parametrize("license_file", ["LICENSE", "HEROICONS_LICENSE.txt"])
def test_wheel_carries_license_file(wheel_names: list[str], license_file: str) -> None:
    assert any(
        ".dist-info/licenses/" in name and name.endswith(license_file)
        for name in wheel_names
    )


def test_wheel_metadata_declares_mit_license_expression(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(
            n for n in archive.namelist() if n.endswith(".dist-info/METADATA")
        )
        metadata = Parser().parsestr(archive.read(metadata_name).decode())

    assert metadata["License-Expression"] == "MIT"
    assert [
        c for c in metadata.get_all("Classifier", []) if c.startswith("License ::")
    ] == []


def test_wheel_has_no_tests_directory(wheel_names: list[str]) -> None:
    assert [name for name in wheel_names if name.startswith("tests/")] == []


@pytest.mark.parametrize("marker", ["node_modules", "reference.css"])
def test_wheel_leaves_out_dev_only_files(wheel_names: list[str], marker: str) -> None:
    assert [name for name in wheel_names if marker in name] == []


@pytest.mark.parametrize(
    "member",
    [
        "panel_framework/__init__.py",
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "pyproject.toml",
    ],
)
def test_sdist_holds_file(sdist: Path, member: str) -> None:
    with tarfile.open(sdist) as archive:
        names = archive.getnames()

    assert any(name.endswith("/" + member) for name in names)
