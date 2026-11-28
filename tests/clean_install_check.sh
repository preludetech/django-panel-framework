#!/bin/sh
# Install a built wheel into a fresh venv and run Django's system checks against it.
# Usage: tests/clean_install_check.sh <path-to-wheel>
set -eu

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT INT TERM
uv venv "$work_dir/venv"
uv pip install --python "$work_dir/venv/bin/python" "$1"
# Run from a directory that holds only the tests, so `panel_framework`
# can come from nowhere but the installed wheel.
cp -r "$(dirname "$0")" "$work_dir/tests"
cd "$work_dir"
venv/bin/python -c "import panel_framework, sys; sys.exit('site-packages' not in panel_framework.__file__)"
venv/bin/python -m django check --settings=tests.standalone_settings
# What the default shell links has to be in the wheel, or an installed page
# renders unstyled and inert.
for asset in css/panel_framework.css vendor/htmx.min.js vendor/alpine-csp.min.js \
    js/shell-components.js js/alpine-components.js; do
    DJANGO_SETTINGS_MODULE=tests.standalone_settings venv/bin/python -m django \
        findstatic "panel_framework/$asset" >/dev/null
done
