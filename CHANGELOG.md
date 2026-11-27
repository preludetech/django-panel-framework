# Changelog

## Deprecation rule

A breaking change keeps the old name, path or setting working for one tag. While it works, it
emits a `DeprecationWarning` subclass with `stacklevel=2`. The next tag removes it.

Each entry opens with a flag block that says what the upgrade asks of a host.

## [0.1.0] - 2026-11-27

```yaml
requires_migrations: true
requires_template_review: false
changed_template_paths: []
requires_settings_change: true
requires_tailwind_rebuild: true
```

First release.

- Import prefix: `panel_framework`. The distribution is `django-panel-framework`.
- App label: `panel_framework`. Its migrations create the bulk action run table.
- System check ids: `panel_framework.E001` to `E008`, `E010`, and `W001` to `W003`.
- Settings: `BULK_BACKGROUND_THRESHOLD`, `PANEL_TABLE_PAGE_SIZE` and
  `PANEL_FRAMEWORK_SITE_RESOLVER`.
- Run `write_panel_framework_css` before every Tailwind build.
