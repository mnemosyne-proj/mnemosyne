# Containerfile for the self-hosted Mnemosyne web app (FastAPI + HTMX).
#
# Build:  podman build -t mnemosyne-web -f Containerfile .
# Run:    podman run --rm -p 8512:8512 -v mnemosyne-data:/data mnemosyne-web
#
# The web app talks only to the Qt-free `libmnemosyne` core, so this image
# deliberately does NOT install PyQt6 or run the `.ui` build step -- that keeps
# it small and avoids needing system Qt libraries.

FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MNEMOSYNE_DATA_DIR=/data

WORKDIR /app

# Runtime dependencies. This mirrors [project].dependencies in pyproject.toml
# *minus* the PyQt6 GUI packages, plus the [web] extra. Debian slim already
# ships libstdc++/libgcc, so the matplotlib/numpy wheels (used for statistics)
# load fine.
RUN pip install --no-cache-dir \
        argon2-cffi cheroot cherrypy matplotlib webob decorator \
        gtts google-trans-new legacy-cgi \
        fastapi "uvicorn[standard]" jinja2 python-multipart

# Application source. No build step / .ui compilation is needed for the web app.
COPY mnemosyne ./mnemosyne
COPY openSM2sync ./openSM2sync

# Run as a non-root user; persist decks and media in a named volume.
RUN useradd --create-home --uid 1000 app \
    && mkdir -p /data \
    && chown -R app:app /data /app
USER app
VOLUME /data
EXPOSE 8512

# Host/data-dir are baked into the entrypoint so they survive arg overrides;
# pass extra flags (e.g. --port) or `-e MNEMOSYNE_AUTH_TOKEN=...` at run time.
ENTRYPOINT ["python", "-m", "mnemosyne.web_app", \
            "--host", "0.0.0.0", "--data-dir", "/data"]
CMD ["--port", "8512"]
