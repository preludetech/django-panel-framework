"""Every name a public module lists in `__all__` exists."""

from __future__ import annotations

import importlib

import pytest

FRAMEWORK = "panel_framework"
PUBLIC_MODULES = [
    "actions",
    "bulk_actions",
    "bulk_runs",
    "config",
    "context",
    "errors",
    "events",
    "filters",
    "forms",
    "housekeeping",
    "lazy_panels",
    "models",
    "panels",
    "quick_view",
    "reference",
    "run_records",
    "tables",
    "testing",
    "testing.template_rules",
    "views",
    "widgets",
]


@pytest.mark.parametrize("module", PUBLIC_MODULES)
def test_every_public_name_exists(module: str) -> None:
    imported = importlib.import_module(f"{FRAMEWORK}.{module}")

    assert [name for name in imported.__all__ if not hasattr(imported, name)] == []
