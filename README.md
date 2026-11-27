# django-panel-framework

Panels for Django: list and instance pages, data tables, filters, actions, bulk runs, a quick
view and dialogs, built on django-cotton, HTMX and Alpine.js.

Requires Python 3.13+ and Django 6.0.x.

## Licence

MIT. See `LICENSE`. The icon SVGs come from Heroicons, also MIT. Its notice is in
`panel_framework/templates/panel_framework/icons/HEROICONS_LICENSE.txt`.

## Contributing

Outside contributions (pull requests, patches) are not accepted for now.

## Install

1. Add the dependency to `pyproject.toml`, pinned to a release tag:

   ```toml
   dependencies = [
       "django-panel-framework @ git+https://github.com/preludetech/django-panel-framework.git@v0.1.0",
   ]
   ```

2. Add the apps to `INSTALLED_APPS`. Put `panel_framework` after any app whose templates
   override the framework's, because the first app in the list wins a template path:

   ```python
   INSTALLED_APPS = [
       # ...
       "django_cotton.apps.SimpleAppConfig",
       "my_theme",  # overrides panel_framework templates
       "panel_framework",
   ]
   ```

3. Include the URLs. They serve the component reference page, which you probably want only
   under `DEBUG`:

   ```python
   if settings.DEBUG:
       urlpatterns += [path("panel-framework/", include("panel_framework.urls"))]
   ```

4. Run `python manage.py migrate`.

5. Run `python manage.py write_panel_framework_css` before every Tailwind build. It writes
   `tailwind.panel_framework.css` into `BASE_DIR`, with an `@source` of the framework's
   templates and an `@import` of its stylesheet. The paths are specific to the machine, so
   don't commit the file. Import its output in your input CSS, after Tailwind:

   ```css
   @import "tailwindcss";
   @import "./tailwind.panel_framework.css";
   ```

6. Set any of these settings you want to change:

   | Setting | Default | Meaning |
   | --- | --- | --- |
   | `BULK_BACKGROUND_THRESHOLD` | `250` | A bulk action over more objects than this runs in a background task. |
   | `PANEL_TABLE_PAGE_SIZE` | `10` | Rows per page for a table with no `page_size` of its own. |
   | `PANEL_FRAMEWORK_SITE_RESOLVER` | `panel_framework.sites.current_site_or_none` | Dotted path of a callable that takes the request and returns its `Site`, or `None`. A project serving several sites from one process must set its own. |

## Host contract

The shell ids, template fragments, context, script order, Tailwind tokens and component
inputs your project provides are in `panel_framework/HOST_CONTRACT.md`.
