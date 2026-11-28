"""The compiled stylesheet in the package is the one its sources build."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TAILWIND = REPO_ROOT / "node_modules" / ".bin" / "tailwindcss"
SOURCE = REPO_ROOT / "panel_framework" / "css" / "standalone.css"
COMPILED = (
    REPO_ROOT
    / "panel_framework"
    / "static"
    / "panel_framework"
    / "css"
    / "panel_framework.css"
)


def test_the_committed_stylesheet_is_what_the_sources_build(tmp_path: Path) -> None:
    """A host installs the stylesheet as committed, with no build of its own.

    A template that gains a utility class, or a rule that changes, has no
    effect on an installed page until the stylesheet is rebuilt.
    """
    assert TAILWIND.exists(), "Tailwind is not installed: run `npm ci`"
    built = tmp_path / "panel_framework.css"

    subprocess.run(  # noqa: S603
        [str(TAILWIND), "--minify", "-i", str(SOURCE), "-o", str(built)],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
    )

    assert built.read_text() == COMPILED.read_text(), (
        "Run `npm run panel_framework_css` and commit the result"
    )
