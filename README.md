# django-panel-framework

Panels for Django: list and instance pages, data tables, filters, actions, bulk runs, a quick
view and dialogs, built on django-cotton, HTMX and Alpine.js.

Requires Python 3.13+ and Django 6.0.x.

## Licence

The framework is MIT. See `LICENSE`. The icon SVGs come from Heroicons, also MIT. Its notice is in
`panel_framework/templates/panel_framework/icons/HEROICONS_LICENSE.txt`. The package also carries
htmx (0BSD) and Alpine.js (MIT) in `panel_framework/static/panel_framework/vendor/`, with their
licences beside them.

## Contributing

Outside contributions (pull requests, patches) are not accepted for now.

## Install

1. Add the dependency to `pyproject.toml`, pinned to a release tag:

   ```toml
   dependencies = [
       "django-panel-framework @ git+https://github.com/preludetech/django-panel-framework.git@v0.2.0",
   ]
   ```

2. Add the apps to `INSTALLED_APPS`:

   ```python
   INSTALLED_APPS = [
       # ...
       "django.contrib.sites",
       "django.contrib.staticfiles",
       "django_cotton.apps.SimpleAppConfig",
       "panel_framework",
   ]
   ```

   `SimpleAppConfig` leaves the template settings to you, so set the loaders and register Cotton's
   tags in `TEMPLATES["OPTIONS"]` (and leave `APP_DIRS` out, because `loaders` replaces it):

   ```python
   "loaders": [
       "django_cotton.cotton_loader.Loader",
       "django.template.loaders.filesystem.Loader",
       "django.template.loaders.app_directories.Loader",
   ],
   "builtins": ["django_cotton.templatetags.cotton"],
   ```

   Set `COTTON_SNAKE_CASED_NAMES = False`: the framework's component files are named with hyphens.

3. Run `python manage.py migrate`.

4. Describe an interface and give it a URL:

   ```python
   # my_app/views.py
   from django.contrib.auth.decorators import login_required
   from django.db.models import QuerySet
   from django.http import HttpRequest, HttpResponse

   from panel_framework.tables import Column, DataTable
   from panel_framework.views import ListViewConfig, NavGroup, panel_framework_view

   from my_app.models import Book


   class BookTable(DataTable):
       search_fields = ["title"]
       default_sort = "title"

       @staticmethod
       def get_queryset(request: HttpRequest) -> QuerySet[Book]:
           return Book.objects.order_by("title")

       @staticmethod
       def get_columns() -> list[Column]:
           return [
               Column(
                   header="Title",
                   template_name="cotton/data-table-cells/text.html",
                   attr="title",
                   sortable=True,
               ),
           ]


   class Books(ListViewConfig):
       url_name = "books"
       menu_label = "Books"
       table_key = "books"
       list_view = BookTable


   @login_required
   def interface(request: HttpRequest, path_string: str = "") -> HttpResponse:
       return panel_framework_view(
           [NavGroup("Library", [Books])],
           request,
           path_string,
           url_name="my_app:interface",
       )
   ```

   ```python
   # my_app/urls.py
   app_name = "my_app"
   urlpatterns = [
       re_path(r"^manage/(?P<path_string>.*)$", views.interface, name="interface"),
   ]
   ```

   `/manage/books` is now a working page: navigation, a searchable and sortable table, and the
   framework's stylesheet and scripts, all served from the package's static files.

## Settings

All optional.

| Setting | Default | Meaning |
| --- | --- | --- |
| `BULK_BACKGROUND_THRESHOLD` | `250` | A bulk action over more objects than this runs in a background task. |
| `PANEL_TABLE_PAGE_SIZE` | `10` | Rows per page for a table with no `page_size` of its own. |
| `PANEL_FRAMEWORK_SITE_RESOLVER` | `panel_framework.sites.current_site_or_none` | Dotted path of a callable that takes the request and returns its `Site`, or `None`. A project serving several sites from one process must set its own. |

## Component reference

`panel_framework.urls` serves a page that shows every component. Include it under `DEBUG`:

```python
if settings.DEBUG:
    urlpatterns += [path("panel-framework/", include("panel_framework.urls"))]
```

## Customising

The defaults need no configuration. `panel_framework/CUSTOMISING.md` covers what you can change:
colours, any template, the page shell, compiling the framework into your own Tailwind build, icons
and components.

## Developing

To change the framework and see the result in your project before you release a tag, see
`DEVELOPING_WITH_A_HOST.md`.

The stylesheet the default shell links is compiled and committed. After changing a template's
classes or a file in `panel_framework/css/`, run `npm ci` once, then `npm run panel_framework_css`,
and commit `panel_framework/static/panel_framework/css/panel_framework.css`. A test fails while the
committed file is stale.
