# Mnemosyne

Mnemosyne is a free, open-source **spaced-repetition flashcard program** that helps you
learn as efficiently as possible. It is also a **research project** into the nature of
long-term memory: you can optionally upload anonymous data about your learning process
(off by default).

## Features

- Spaced-repetition scheduling, plus a separate cramming scheduler and pluggable schedulers
- Rich flashcards (images, audio, video, LaTeX) and powerful card types
- Bi-directional sync across devices, and review through a browser via a built-in web server
- Flexible card browser, statistics and learning visualizations
- Google text-to-speech and translate support
- Plugin architecture, external scripting, and a core library for building your own front-end

More detail is on the [features page](https://mnemosyne-proj.org/features) and in the
[documentation](https://mnemosyne-proj.org/help/index.php).

> The web server does **not** implement any authentication or security features.

## Supported platforms

Desktop clients for **Windows, macOS and Linux**, and a separate **Android** client.

To just use Mnemosyne, download a release from the
[download page](https://mnemosyne-proj.org/download-mnemosyne.php). The rest of this file
is for developers.

## Development environment

The project uses [devenv](https://devenv.sh) (Nix) to provide the system libraries Qt6
needs, and [uv](https://docs.astral.sh/uv/) to manage Python dependencies (Python 3.13+).

```sh
devenv shell      # enter the dev shell (provides Qt6 native libs, Python, uv)
uv sync           # install Python deps from uv.lock into .venv
make build        # compile the Qt .ui files
uv run mnemosyne  # launch the app
```

Without devenv, install the equivalent system libraries yourself (Qt6/PyQt6 runtime
deps — GL, the X11/XCB stack, glib, etc.; see `devenv.nix` for the full list) and a
recent `uv`, then run the `uv`/`make` steps above.

### Running the tests

```sh
make test         # runs pytest and writes test-results.xml
```

Run a single test with:

```sh
uv run pytest tests/<file>.py::<class>::<method>
```

`./tools/convert_junitxml.py` converts `test-results.xml` into a plain-text todo list.

## Building installers

The `makefile` has targets for building distributable apps: `make macos` (requires a
`CODESIGN_IDENTITY`), `make windows-installer`, and `make android`. See the makefile for
details.

## Contributing

Fork the repo, work on a feature branch, make sure the test suite passes, rebase onto an
up-to-date `master`, and open a pull request. Please follow the standard Python style
guides, [PEP8](https://peps.python.org/pep-0008/) and
[PEP257](https://peps.python.org/pep-0257/). For an overview of how the code fits
together, build the docs (`make build-docs`) and read
`mnemosyne/libmnemosyne/docs/build/html/index.html`.
