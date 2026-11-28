# Customising

The framework works as installed. The default shell (`panel_framework/shell/base.html`) loads the
framework's stylesheet and scripts and renders every region a panel page needs, and
`panel_framework_view` uses it unless you name another template. Nothing on this page is required.
Each section covers one thing you can change.

## Colours

The compiled stylesheet declares each colour role as a CSS variable on `:root`. To change a colour,
set the variable in a stylesheet loaded after the framework's:

```css
:root {
    --color-primary: #7c3aed;
    --color-sidepanel: #f5f3ff;
}
```

Load that stylesheet from the `head_extra` block of a template that extends
`panel_framework/shell/base.html`. `on-*` is the foreground on the matching background. The hover
roles and `focus-ring` follow the role they are mixed from unless you set them.
`css/default_theme.css` holds the default values. A test keeps this block equal to that file.

```
--color-primary
--color-on-primary
--color-secondary
--color-accent
--color-on-accent
--color-success
--color-on-success
--color-warning
--color-error
--color-on-error
--color-info
--color-success-light
--color-warning-light
--color-error-light
--color-info-light
--color-on-success-light
--color-on-warning-light
--color-on-error-light
--color-on-info-light
--color-primary-hover
--color-accent-hover
--color-success-hover
--color-error-hover
--color-surface
--color-surface-2
--color-on-surface
--color-border
--color-muted
--color-focus-ring
--color-sidepanel
```

`--panel-table-head`, `--sidebar-top` and the `--modal-*` variables are internal to the framework.

## Templates

Django uses the first template it finds for a path: a `DIRS` entry beats every app, and apps resolve
in `INSTALLED_APPS` order. To replace a framework template, add one at the same path in an app
listed before `panel_framework`.

The shell is built from small templates in `panel_framework/shell/`, so you override the piece you
want to change:

| Template | Holds |
| --- | --- |
| `base.html` | the whole document, with blocks `head_title`, `styles`, `scripts`, `alpine_components`, `head_extra`, `messages`, `navigation`, `content_header`, `content` and `overlays` |
| `styles.html` | the link to the compiled stylesheet |
| `scripts.html` | htmx, its configuration and the framework's Alpine components |
| `alpine.html` | Alpine's CSP build |
| `toasts.html` | the two toast regions and Django's `messages` |
| `navigation.html` | the navigation `<dialog>` |
| `sidebar.html` | what the navigation holds: by default, the menu alone |
| `overlays.html` | the quick view, the modal dialog and the screen-reader announcer |

Two common changes:

- A logo above the menu: override `panel_framework/shell/sidebar.html`.
- An Alpine component of your own: extend `base.html` and load its script in the
  `alpine_components` block. Alpine's CSP build takes no inline expressions, so a component is
  registered from a script, and that script loads before Alpine.

Context the shell reads, all optional:

- `site_name`, from a context processor of yours. The document title ends with it.
- `request.panel_scope_name`. The document title names the scope.
- `request.panel_url_kwargs`, a dict. The framework adds these kwargs whenever it reverses a panel
  URL, for a host whose panel URLs carry one (an organisation slug, say).

## Your own shell

A project with its own base template passes it to the view:

```python
panel_framework_view(
    config,
    request,
    path_string,
    template_name="my_app/interface.html",
    url_name="my_app:interface",
)
```

That template includes the pieces in this order:

```django
<head>
    <title>{% include "panel_framework/partials/document_title.html#document-title" %}</title>
    {% include "panel_framework/shell/styles.html" %}
    {% include "panel_framework/shell/scripts.html" %}
    {# your own Alpine component scripts #}
    {% include "panel_framework/shell/alpine.html" %}
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    {% include "panel_framework/shell/toasts.html" %}
    <div x-data="sidePanel" data-storage-key="my-sidebar" data-desktop-lock="true">
        <div class="side-panel-grid grid relative">
            {% include "panel_framework/shell/navigation.html" %}
            <main id="interface-main">
                {% include "panel_framework/partials/breadcrumbs.html" %}
                {% include "panel_framework/partials/page_title.html" %}
                {% include main_template_name with main=main request=request csrf_token=csrf_token only %}
            </main>
        </div>
        {% include "panel_framework/shell/overlays.html" %}
    </div>
</body>
```

What each part is for:

- `hx-headers` on `<body>` sends the CSRF token with every htmx request. Without it every htmx POST
  answers 403.
- The `sidePanel` wrapper holds the navigation and the main region, because the menu toggle in each
  page header belongs to it.
- `#interface-main` holds the page. The overlays sit outside it, so an open dialog survives an htmx
  swap of the page.
- A project that already loads htmx 2.x and Alpine's CSP build leaves out `scripts.html` and
  `alpine.html` and loads `panel_framework/js/shell-components.js`, then
  `panel_framework/js/alpine-components.js`, before Alpine.

The framework's scripts and fragments find these elements by id. Don't reuse one in your markup:
`#interface-main`, `#main-content`, `#instance-header`, `#sidebar-nav`, `#breadcrumbs`,
`#page-title`, `#app-modal`, `#app-modal-body`, `#quick-view*`, `#scope-announcer`,
`#toast-region-polite`, `#toast-region-assertive`.

## Your own Tailwind build

A project that builds its own Tailwind stylesheet can compile the framework into it, in place of
`shell/styles.html`. The framework's rules then use the project's theme tokens at build time.
Tailwind 4.1.16 or later.

1. Run `python manage.py write_panel_framework_css` before every Tailwind build. It writes
   `tailwind.panel_framework.css` into `BASE_DIR`, holding a `@source` of the framework's templates
   and an `@import` of `css/panel_framework.css`. The paths are machine-specific, so don't commit the
   file, and rerun the command after installing or upgrading the framework.
2. In the input CSS, add `@import "./tailwind.panel_framework.css";` after `@import "tailwindcss"`
   and the theme tokens, and before any rule that reopens a framework class such as
   `.panel-surface`.
3. Define every role in [Colours](#colours) in the theme, under the same `--color-<role>` names.
4. Supply base element styles for `table`, `th`, `td`, `h1` and `h2`. Framework templates leave
   cell padding and colour, and heading size and weight, to the page. The default shell's rules are
   in `css/shell.css`, under `@layer base`, with its navigation layout above them.

## Icons

The framework draws every icon through its own `c-panel-icon` primitive, which takes `name`, `class`
and `aria_label`. The default includes the icon's paths from `panel_framework/icons/<name>.html` inside
a 24 by 24 `<svg>`. The framework ships one such body template for every name in this block. The block
equals `REQUIRED_ICON_NAMES` in `checks.py`. The bodies are Heroicons outline icons (MIT, see
`templates/panel_framework/icons/HEROICONS_LICENSE.txt`).

```
add
boolean_false
boolean_true
check
close
download
dropdown
error
filter
info
loading
menu
more_options
next
open_page
previous
quick_view
retry
search
settings
sort_asc
sort_desc
sort_neutral
success
trend_down
trend_up
user
warning
```

You change the icons by template path:

- To add an icon, add `panel_framework/icons/<name>.html` holding its paths. Names that host data
  supplies (a sidebar item's `icon`, an empty state's `icon`, a button's `icon_left`) belong to the
  host and need a body each. A name with no body raises `TemplateDoesNotExist`.
- To replace one icon, put a template of the same name earlier in template precedence.
- To use the host's own icon component for all of them, override `cotton/panel-icon.html` with a
  wrapper that forwards to it. The
  override must draw every name in the block.

`manage.py check` renders each name through `c-panel-icon`, the framework's or the host's override. A
name that raises is error `panel_framework.E010`. A name that renders nothing is warning
`panel_framework.W003`.


## Primitives

Each primitive is a Cotton component in `templates/cotton/`. A host overrides one by putting a template
of the same name earlier in template precedence: a `DIRS` entry beats every app, and apps resolve in
`INSTALLED_APPS` order. The usual override is a thin wrapper that forwards every prop, slot and
`{{ attrs }}` to the host's own component. An override keeps the hooks in its row, because the
framework's JavaScript and stylesheet select on them.

| Primitive | Props | Slots | Hooks an override keeps | Thin wrapper |
| --- | --- | --- | --- | --- |
| `panel-button` (`panel-button.html`) | `variant` `type` `href` `form` `id` `name` `value` `disabled` `autofocus` `aria_label` `aria_describedby` `dropdown` `class` `tone` `size` `icon_left` `icon_right` `loading` `loading_text` | default | classes `panel-btn`, `panel-btn-<variant>`, `panel-btn-sm`, or the host's own button classes with the framework's `.panel-btn` rules copied onto them (see below); `data-variant`; `data-loading-label` on the loading span | `<c-button :variant="variant" :href="href" :attrs="attrs">{{ slot }}</c-button>` |
| `panel-button-group` (`panel-button-group.html`) | `variant` `class` | default | none | `<c-button-group :variant="variant" :class="class">{{ slot }}</c-button-group>` |
| `panel-chip` (`panel-chip.html`) | `variant` `size` `icon` `class` | default | classes `panel-chip`, `panel-chip-<variant>`, `panel-chip-<size>` | `<c-chip :variant="variant" :size="size" :icon="icon" :attrs="attrs">{{ slot }}</c-chip>` |
| `panel-callout` (`panel-callout.html`) | `tone` `title` `class` | default | `role="alert"` on `error` and `role="status"` on `success`; extra attributes pass through `{{ attrs }}` | `<c-callout :tone="tone" :title="title" :class="class" :attrs="attrs">{{ slot }}</c-callout>` |
| `panel-back-link` (`panel-back-link.html`) | `href` `class` | default | the anchor passes `hx-*` attributes through `{{ attrs }}`; `breadcrumbs.html` relies on it | `<c-back-link :href="href" :attrs="attrs">{{ slot }}</c-back-link>` |
| `panel-pagination` (`panel-pagination.html`) | `page_obj` `base_url` `table_id` `sort_by` `sort_order` `search_query` `extra_params` `page_param_name` `push_url` `links` `page_url` `class` | none | the `hx-get`, `hx-target` and `hx-push-url` attributes on each page control; class `panel-pagination` | `<c-pagination :page_obj="page_obj" :base_url="base_url" :table_id="table_id" :links="links" />` |
| `panel-dropdown-menu` (`panel-dropdown-menu.html`) | `trigger` `class` `aria_label` `menu_label` `trigger_variant` `trigger_size` `panel_class` | default; `trigger` as a named slot | an Alpine component on the wrapper (`panelDropdownMenu`, or the host's own) with `x-ref` `menuButton` and `menuPanel`; the `role="menu"` wrapper | `<c-dropdown-menu :aria_label="aria_label" :class="class">{{ slot }}</c-dropdown-menu>` |
| `panel-dropdown-menu-separator` (`panel-dropdown-menu-separator.html`) | none | none | `role="separator"`, which keeps it out of the arrow-key order | `<c-dropdown-menu-separator />` |
| `panel-icon` (`panel-icon.html`) | `name` `class` `aria_label` | none | `aria-hidden="true"` without `aria_label`, `role="img"` and `aria-label` with one | `<c-icon :name="name" :class="class" :aria_label="aria_label" />` |
| `panel-page` (`panel-page.html`) | `width` `flush` `class` | default | none | `<c-page :width="width" :flush="flush" :class="class">{{ slot }}</c-page>` |
| `panel-date` (`panel-date.html`) | `value` `short` | none | `<time datetime>` | `<c-date :value="value" :short="short" />` |
| `panel-datetime` (`panel-datetime.html`) | `value` | none | `<time datetime>` and the two `whitespace-nowrap` spans | `<c-datetime :value="value" />` |

Notes that do not fit a row:

- `panel-button`: a wrapper that draws its own button classes instead of `panel-btn` copies three
  framework rules onto them, or the framework's buttons lose them: the small size inside
  `.panel-data-table td` and `.panel-data-table-card`, the small size inside `[data-modal-footer]`
  below md (`max-md:px-2 max-md:py-1.5 max-md:text-sm`, with no height set, so the footer's buttons
  match every other small button on a phone), and `whitespace-nowrap` inside
  `.panel-data-table-actions`. A host whose button class differs copies them onto its own.
- `panel-dropdown-menu`: `trigger_variant` and `trigger_size` are the trigger button's `variant` and
  `size`. A wrapper maps them to whatever its own button takes. The framework passes `size="small"` to
  get the small button.
- `panel-callout` serves pages, panels and dialogs alike. `tone` is `info` (default), `success`,
  `warning` or `error`; any other value renders as `info`. It is the only way a template shows an
  error, a warning or a failed request; no template writes `role="alert"` or error-coloured text.
  A wrapper must pass `{{ attrs }}` to its root: `partials/request_error.html` sets `hidden`,
  `tabindex`, `data-request-error` and `data-request-error-message` there, and the framework's
  script shows the box and sets the text of its `[data-request-error-text]` child. A form or dialog
  of your own includes that partial (`message` replaces the generic text) and never writes a
  holder. A field's own error is `partials/field_error.html` (`field`, optional `extra_class`).
- Everything on the canvas sits inside a box. `panel-card` and a boxed `panel-stat-tile` set
  `data-panel-box` on their root; a page template of your own puts every notice, paragraph,
  button and empty state inside one. `assert_canvas_holds_only_boxes` in
  `tests/playwright/assertions.py` checks a loaded page. A list page's `intro_template_name`
  renders inside the list's card, above the toolbar; the card is flush, so the template pads
  itself.
- `panel-date` with `short` always renders the day and month ("3 Nov") and no year. `panel-date` and
  `panel-datetime` format with Django's `date` filter (`j M Y`, and `H:i` for the time) in the current
  time zone.


## Reference page

The DEBUG-only component reference page extends `panel_framework/reference/base.html`, which extends
the default shell. To give the page your own shell, override that template by path. The override
defines two blocks: `head_title`, the page's `<title>` text, and `content`, where the page renders.
