"""Root URL configuration for panel_framework tests."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("test-panel/", include("tests.urls")),
    # So `admin:login` reverses: staff_member_required redirects there, and
    # the reference-page tests need that redirect to resolve.
    path("admin/", admin.site.urls),
]
