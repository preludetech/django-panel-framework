import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The package and its tests: no file in either imports the Freedom LS project.
SCANNED_DIRECTORIES = ("panel_framework", "tests")


def _is_foreign(module: str) -> bool:
    return module == "freedom_ls" or module.startswith("freedom_ls.")


def foreign_imports(path: Path) -> list[str]:
    """Each import in `path` of a freedom_ls module,
    as "<path>:<line>: <import>"."""
    found: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_foreign(alias.name):
                    found.append(f"{path}:{node.lineno}: import {alias.name}")
        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module
            and _is_foreign(node.module)
        ):
            found.append(f"{path}:{node.lineno}: from {node.module} import ...")
    return found


def framework_files() -> list[Path]:
    """Every .py file under the package and its tests."""
    return [
        path
        for directory in SCANNED_DIRECTORIES
        for path in sorted((REPO_ROOT / directory).rglob("*.py"))
    ]


def test_the_package_and_its_tests_import_no_freedom_ls_module() -> None:
    found = [line for path in framework_files() for line in foreign_imports(path)]

    assert found == []


@pytest.mark.parametrize(
    ("source", "reported"),
    [
        ("from freedom_ls.base import csv_safety\n", True),
        ("import freedom_ls.base.csv_safety\n", True),
        ("import freedom_ls\n", True),
        ("from panel_framework import models\n", False),
        ("from . import helpers\n", False),
        ("import freedom_ls_other\n", False),
    ],
)
def test_foreign_imports_reports_only_freedom_ls_modules(
    tmp_path: Path, source: str, reported: bool
) -> None:
    # Arrange
    module = tmp_path / "module.py"
    module.write_text("x = 1\n" + source)

    # Act
    found = foreign_imports(module)

    # Assert
    if reported:
        assert len(found) == 1
        assert found[0].startswith(f"{module}:2: ")
    else:
        assert found == []


def test_framework_files_cover_migrations_and_every_test_directory() -> None:
    files = framework_files()

    assert any("migrations" in path.parts for path in files)
    assert any(path.parent == REPO_ROOT / "tests" for path in files)
    for directory in ("tests/components", "tests/invariants", "tests/playwright"):
        assert any(path.is_relative_to(REPO_ROOT / directory) for path in files)
