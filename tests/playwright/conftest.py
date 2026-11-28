"""Browser-test setup for panel_framework."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlparse

import pytest
import pytest_django.live_server_helper
from playwright.sync_api import Playwright

from django.contrib.sites.models import Site
from django.db import connections

import panel_framework


@pytest.fixture(scope="session")
def playwright(playwright: Playwright) -> Iterator[Playwright]:
    """pytest-playwright's ``playwright``, closing DB connections before it stops.

    Playwright's sync API leaves its loop marked as running on the main thread,
    so Django stores the thread's connections in contextvar storage rather than
    the thread-local one. Once Playwright stops and the loop is cleared, nothing
    can see those connections to close them, and the open session makes
    pytest-django's ``DROP DATABASE`` fail with "being accessed by other users".
    """
    yield playwright
    connections.close_all()


@pytest.fixture
def live_server_site(
    live_server: pytest_django.live_server_helper.LiveServer, site: Site
) -> Site:
    """The test ``Site``, with its domain set to the live server's host.

    The live server resolves the current site from the request host, so the
    site row must carry the host the browser connects to.
    """
    site.domain = urlparse(live_server.url).netloc
    site.save()
    return site


@pytest.fixture(autouse=True)
def _no_htmx_settle_window(request: pytest.FixtureRequest) -> None:
    """Remove htmx's 20ms settle delay from every page a flow opens.

    The stub host answers fast enough that a flow's next click can land inside
    the settle window of the swap before it, and htmx drops a request started
    from an element that is still settling. A user cannot click that fast, so
    the window only makes the flows flaky.
    """
    if "page" not in request.fixturenames:
        return
    page = request.getfixturevalue("page")
    page.add_init_script(
        "document.addEventListener('htmx:load', () => {"
        " window.htmx.config.defaultSettleDelay = 0; }, { once: true });"
    )
