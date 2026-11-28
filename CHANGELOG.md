# Changelog

## Deprecation rule

A breaking change keeps the old name, path or setting working for one tag. While it works, it
emits a `DeprecationWarning` subclass with `stacklevel=2`. The next tag removes it.

Each entry opens with a flag block that says what the upgrade asks of a host.

## [0.2.0] - 2026-11-28

```yaml
requires_migrations: false
requires_template_review: true
changed_template_paths:
  - panel_framework/minimal_shell.html
  - panel_framework/reference/base.html
requires_settings_change: false
requires_tailwind_rebuild: true
```

The framework works as installed. A host adds the apps and one URL that calls
`panel_framework_view`.

- `panel_framework_view` no longer needs `template_name`. It defaults to the new shell,
  `panel_framework/shell/base.html`. `url_name` is now keyword-only.
- The shell is split into templates under `panel_framework/shell/`, each overridable by path.
  `panel_framework/minimal_shell.html` still renders the shell for this release and goes in the
  next.
- The package ships a compiled stylesheet, `static/panel_framework/css/panel_framework.css`, with
  the default colour roles as CSS variables. `write_panel_framework_css` stays for a host that
  compiles the framework into its own Tailwind build.
- The package ships htmx 2.0.8 and Alpine's CSP build 3.15.8 in `static/panel_framework/vendor/`.
- `alpine-components.js` now swaps a 422, a marked 403 or 404, and an error response that carries a
  toast. A host no longer needs its own `htmx:beforeSwap` listener for them.
- `css/panel_framework.css` now defines `[x-cloak]` and hides `[data-selection-bar-pending]`. A host
  that compiles the framework can delete its own copies.
- Renamed: `css/reference_theme.css` to `css/default_theme.css`, `css/minimal_shell.css` to
  `css/shell.css`, and `HOST_CONTRACT.md` to `CUSTOMISING.md`. The check hint for
  `panel_framework.E010` follows.

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
- System check ids: `panel_framework.E001` to `E010`, and `W001` to `W003`.
- Settings: `BULK_BACKGROUND_THRESHOLD`, `PANEL_TABLE_PAGE_SIZE` and
  `PANEL_FRAMEWORK_SITE_RESOLVER`.
- Run `write_panel_framework_css` before every Tailwind build.
