#
# __main__.py <lucascontre95@gmail.com>
#

"""Command-line entry point: `mnemosyne-web` / `python -m mnemosyne.web_app`."""

import argparse
import os

from mnemosyne.web_app.app import Settings, create_app


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="mnemosyne-web",
        description="Self-hosted Mnemosyne web app (FastAPI + HTMX).")
    parser.add_argument(
        "--data-dir", default=os.environ.get("MNEMOSYNE_DATA_DIR"),
        help="Directory holding the Mnemosyne database(s) and media. "
             "Defaults to the standard per-OS Mnemosyne data dir when "
             "omitted.")
    parser.add_argument(
        "--config-dir", default=os.environ.get("MNEMOSYNE_CONFIG_DIR"),
        help="Config directory (defaults to the data dir).")
    parser.add_argument(
        "--database", default=None,
        help="Path of the .db deck to open on startup.")
    parser.add_argument("--host", default="127.0.0.1",
        help="Bind address. Use 0.0.0.0 to expose on the network "
             "(consider --auth-token when you do).")
    parser.add_argument("--port", type=int, default=8512)
    parser.add_argument(
        "--auth-token", default=os.environ.get("MNEMOSYNE_AUTH_TOKEN"),
        help="Optional shared secret required on every request.")
    args = parser.parse_args(argv)

    # A None data_dir is fine: libmnemosyne falls back to the per-OS default.
    settings = Settings(
        data_dir=args.data_dir,
        config_dir=args.config_dir,
        filename=args.database,
        host=args.host,
        port=args.port,
        auth_token=args.auth_token,
    )

    import uvicorn
    app = create_app(settings)
    # Single worker: the core is single-threaded by design.
    uvicorn.run(app, host=settings.host, port=settings.port, workers=1)


if __name__ == "__main__":
    main()
