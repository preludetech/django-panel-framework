# Developing the framework alongside a host project

Use this setup when you change django-panel-framework and need to see the change in a project
that uses it (the host).

## The idea

- **Committed state is a release tag.** The host's `pyproject.toml` pins a tag and its `uv.lock`
  records the commit. CI, Docker and every other machine install exactly that.
- **Local state is an editable link.** On your machine, the host's venv has a local checkout of
  the framework installed editable over the locked copy. Edits show up straight away, and nothing
  about the link is committed.

Rejected alternatives:

- A path entry in `[tool.uv.sources]`: it's a committed change, and `uv sync --locked` fails on any
  machine without that path.
- `PYTHONPATH`: it shadows the installed copy silently, so it's easy to forget it's on.
- `uv run --with-editable` on every command: it works, but has to be typed on every command.
  Keep it for one-off runs.

## Setup

### 1. Pin a tag in the host

```toml
dependencies = [
    "django-panel-framework @ git+https://github.com/preludetech/django-panel-framework.git@v0.1.0",
]
```

Use the PEP 508 form in `[project].dependencies`, not `[tool.uv.sources]`. Tools that read only
`[project].dependencies` (`uv pip install -r pyproject.toml`, a project that installs the host as
a dependency) see it too. CI and Docker images need `git` installed to fetch it.

### 2. Link a local checkout

From the host's root, after every `uv sync`:

```sh
uv sync
uv pip install --no-deps -e /path/to/django-panel-framework
```

`uv sync` puts the locked copy back, so link again after every sync. Put both lines in the host's
setup or rebuild script.

`--no-deps` keeps the host's dependencies exactly as locked. If your framework change adds a
dependency, the host gets it when you bump the pin (step 5). Until then, `uv pip install` it by
hand.

After linking, run `python manage.py write_panel_framework_css` and rebuild Tailwind. The
generated file holds the framework's template path, and that path has just changed.

### 3. Stop `uv run` undoing the link

By default `uv run` syncs the venv before every command, and that removes the editable install.
The host's pre-commit hook is a `uv run` too, if it uses one. Set `UV_NO_SYNC=1` for the host
project only.

With [direnv](https://direnv.net/), put this in an `.envrc` in the host's root, or in the
directory that holds all its worktrees:

```sh
export UV_NO_SYNC=1
```

Then run `direnv allow` there. Don't set it in a global shell profile: it would stop `uv run`
syncing in every other uv project on the machine.

With `UV_NO_SYNC` on, `uv run` never installs new host dependencies. Run `uv sync` and link again
(step 2) after pulling a change to `pyproject.toml` or `uv.lock`.

Coding agents launched from inside the host's directory inherit the variable. For Claude Code
launched some other way, such as from an IDE, also add `"env": {"UV_NO_SYNC": "1"}` to the host's
untracked `.claude/settings.local.json`.

### 4. Check the link

```sh
uv run --no-sync python -c "import panel_framework; print(panel_framework.__file__)"
```

It should print a path inside your checkout. A path under `.venv/.../site-packages` means the
locked copy is in use: link again.

### 5. Release a change to the host

1. Commit the change in the framework, tag it and push the tag.
2. In the host, bump the tag in `pyproject.toml`, run `uv lock`, and run the host's tests, all in
   one host change.

Before the host change merges, the linked checkout should be at the commit `uv.lock` records,
with nothing uncommitted. Otherwise your local tests ran against code CI won't install. A check
in the host's pre-merge script can enforce this. Run it with `.venv/bin/python`, not `uv run`,
so a sync can't swap the link out before the check sees it.

## Optional: paired worktrees

If the host uses git worktrees, give the framework a worktree with the same branch name and have
the host's link step pick it, falling back to the locked copy when there isn't one:

```sh
dir="${PANEL_FRAMEWORK_DIR:-$PANEL_FRAMEWORK_REPO/$(git branch --show-current)}"
if [ -f "$dir/pyproject.toml" ]; then
    uv pip install --no-deps -e "$dir"
    export UV_NO_SYNC=1
else
    echo "No framework worktree at $dir: the locked copy stays in use."
fi
```

Create the framework worktree by hand:
`git -C "$PANEL_FRAMEWORK_REPO" worktree add "<branch>" -b "<branch>"`.
