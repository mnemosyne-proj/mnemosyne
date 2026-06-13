# Mnemosyne web app (self-hosted)

A self-hostable web front-end for Mnemosyne, built with **FastAPI** + **HTMX**
+ **_hyperscript** (minimal JavaScript, no build step). It drives the same
`libmnemosyne` domain layer as the desktop and legacy web clients, so reviews,
edits and scheduling stay fully compatible.

The styling is a **shadcn/ui-inspired** design system hand-ported to plain CSS
(`static/app.css`) -- the same neutral palette, design tokens, radius and
component look as shadcn, with a light/dark toggle -- without React, Tailwind
or a build step.

It is a **single-user** server: one person, who may keep **multiple decks**
(`.db` files) and switch between them. There is no multi-user login and no
built-in sync — the server owns its own data directory.

## Install

The web app is an opt-in extra so the desktop build is unaffected:

```sh
uv sync --extra web
```

(That installs `fastapi`, `uvicorn`, `jinja2` and `python-multipart`. The web
app itself needs **no PyQt6** — it only uses the Qt-free core. Statistics PNGs
use the `matplotlib` that ships with the base install.)

## Run

```sh
uv run mnemosyne-web --data-dir ~/mnemosyne-web --port 8512
# then open http://127.0.0.1:8512
```

- `--data-dir` holds the deck(s) and media. Omit it to use the standard per-OS
  Mnemosyne data dir.
- `--database FILE.db` opens a specific deck on startup.
- It binds to `127.0.0.1` by default. To expose it on your network pass
  `--host 0.0.0.0`, and protect it with a shared secret:

```sh
uv run mnemosyne-web --host 0.0.0.0 --auth-token "$(openssl rand -hex 16)"
```

When `--auth-token` (or `MNEMOSYNE_AUTH_TOKEN`) is set, every request must send
the token via the `X-Auth-Token` header or an `auth_token` cookie.

## Run with a container (Podman / Docker)

A `Containerfile` at the repository root builds a small image that runs **only**
the web app — it installs the Qt-free runtime dependencies (no PyQt6, no `.ui`
build step), so the image stays lean. Statistics work too, since the Debian-slim
base ships the C libraries matplotlib/numpy need.

Build (from the repository root):

```sh
podman build -t mnemosyne-web -f Containerfile .
# or: docker build -t mnemosyne-web -f Containerfile .
```

Run, persisting your decks in a named volume:

```sh
podman run --rm -p 8512:8512 -v mnemosyne-data:/data mnemosyne-web
# then open http://127.0.0.1:8512
```

- Decks and media live in the `/data` volume (`MNEMOSYNE_DATA_DIR=/data`).
- The server already binds `0.0.0.0` inside the container; map the port with
  `-p HOST_PORT:8512`.
- Enable auth without changing the command:

  ```sh
  podman run --rm -p 8512:8512 -v mnemosyne-data:/data \
      -e MNEMOSYNE_AUTH_TOKEN="$(openssl rand -hex 16)" mnemosyne-web
  ```

- Open a specific deck or change the port by appending flags (the `--host` and
  `--data-dir` defaults are baked into the entrypoint and kept):

  ```sh
  podman run --rm -p 9000:9000 -v mnemosyne-data:/data mnemosyne-web \
      --port 9000 --database spanish.db
  ```

## Features

- **Review** — study loop with show-answer / grade 0–5, keyboard shortcuts.
- **Browse** — searchable, paginated card list.
- **Add / edit / delete** cards (card-type-aware forms).
- **Tags** — rename and delete.
- **Decks** — list, create and switch `.db` files; view a deck's saved sets.
- **Statistics** — the core's statistics pages, rendered as PNG / HTML.
- **Import / Export** — every libmnemosyne file format (TSV, Anki, Mnemosyne
  formats, …).
- **Settings** — a curated subset of configuration.

## Design notes

`libmnemosyne` keeps a single SQLite connection and is not thread-safe, so
`core_service.CoreService` owns one `Mnemosyne` instance on a single worker
thread and funnels every domain call through a 1-worker executor
(`await core.call(lambda m: ...)`). Run with a single uvicorn worker.

### Current limitations

- Editing a card keeps its card type fixed (changing card type needs a field
  correspondence map, which the web form does not yet collect).
- The browser searches the whole deck in Python; fine for personal-scale decks.
- Statistics show each page's default variant (no variant selector yet).

## Tests

```sh
uv run python -m pytest tests/test_web_app.py
```

The tests boot the real core against a temp data dir and exercise the HTTP
endpoints; no Qt is required. (The statistics-PNG test is skipped in
environments where matplotlib/numpy C-extensions can't load.)
