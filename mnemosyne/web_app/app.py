#
# app.py <lucascontre95@gmail.com>
#

"""FastAPI application factory for the self-hosted Mnemosyne web app."""

import os
import secrets
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from mnemosyne.web_app.core_service import CoreService
from mnemosyne.web_app.templating import templates
from mnemosyne.web_app.routers import (review, browse, cards, tags, decks,
                                       stats, impexp, config as config_router)

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")


@dataclass
class Settings:
    # When None, libmnemosyne falls back to the standard per-OS data dir.
    data_dir: Optional[str] = None
    config_dir: Optional[str] = None
    filename: Optional[str] = None
    host: str = "127.0.0.1"
    port: int = 8512
    # Optional shared secret; when set, every request must carry it (single
    # user, so no user table). Off by default for localhost use.
    auth_token: Optional[str] = None


def create_app(settings: Settings) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        core = CoreService(settings.data_dir, settings.config_dir,
                           settings.filename)
        await core.start()
        app.state.core = core
        try:
            yield
        finally:
            await core.stop()

    app = FastAPI(title="Mnemosyne", lifespan=lifespan)
    app.state.settings = settings
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(review.router)
    app.include_router(browse.router)
    app.include_router(cards.router)
    app.include_router(tags.router)
    app.include_router(decks.router)
    app.include_router(stats.router)
    app.include_router(impexp.router)
    app.include_router(config_router.router)

    if settings.auth_token:
        token = settings.auth_token

        @app.middleware("http")
        async def require_token(request: Request, call_next):
            # Allow static assets through so the login page can render.
            if request.url.path.startswith("/static/"):
                return await call_next(request)
            supplied = (request.headers.get("x-auth-token")
                        or request.cookies.get("auth_token", ""))
            if not secrets.compare_digest(supplied, token):
                # Return directly: HTTPException raised in middleware is not
                # processed by the exception handlers.
                return PlainTextResponse("Unauthorized", status_code=401)
            return await call_next(request)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        core: CoreService = request.app.state.core

        def snapshot(m):
            scheduled, not_memorised, active = m.review_controller().counters()
            return {
                "database": os.path.basename(
                    m.config()["last_database"] or "default.db"),
                "scheduled": scheduled,
                "not_memorised": not_memorised,
                "active": active,
            }

        info = await core.call(snapshot)
        return templates.TemplateResponse(
            request, "index.html", {"info": info})

    @app.get("/media/{path:path}")
    async def media(request: Request, path: str):
        core: CoreService = request.app.state.core
        media_dir = core.media_dir
        if not media_dir:
            raise HTTPException(status_code=404)
        # Resolve and confine to the media dir (no path traversal).
        full = os.path.normpath(os.path.join(media_dir, path))
        if not full.startswith(os.path.abspath(media_dir) + os.sep):
            raise HTTPException(status_code=404)
        if not os.path.isfile(full):
            raise HTTPException(status_code=404)
        return FileResponse(full)

    return app
