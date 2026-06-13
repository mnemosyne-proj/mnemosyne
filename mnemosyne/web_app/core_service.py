#
# core_service.py <lucascontre95@gmail.com>
#

"""Bridge between the async FastAPI world and the synchronous, *single
connection* `libmnemosyne` core.

`libmnemosyne` keeps one SQLite connection and is not thread-safe (the legacy
web server runs with `numthreads=1` for exactly this reason). We therefore own
the `Mnemosyne` instance from a single dedicated worker thread and funnel every
domain call through a 1-worker executor. This both serialises access and keeps
the SQLite connection pinned to the thread that created it.

Routers never touch the core directly; they `await core.call(lambda m: ...)`.
"""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from mnemosyne.libmnemosyne import Mnemosyne as MnemosyneBase


class WebMnemosyne(MnemosyneBase):

    """The `Mnemosyne` factory wired up with our web front-end components.

    Same recipe as `mnemosyne/web_server/web_server.py:load_mnemosyne`, but
    plugging in `web_app`'s widgets instead of the review-only ones.
    """

    def __init__(self):
        super().__init__(upload_science_logs=False,
                         interested_in_old_reps=True)
        self.components.insert(0,
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator",
             "GetTextGuiTranslator"))
        self.components.append(
            ("mnemosyne.web_app.frontend", "WebMainWidget"))
        # Reuse the legacy web render chain (browser-friendly card HTML/media).
        self.components.append(
            ("mnemosyne.web_server.web_server_render_chain",
             "WebServerRenderChain"))
        for study_mode in ("ScheduledForgottenNew", "NewOnly",
                           "CramAll", "CramRecent"):
            self.gui_for_component[study_mode] = [
                ("mnemosyne.web_app.frontend", "WebReviewWidget")]


class CoreService:

    """Owns the `WebMnemosyne` instance and serialises access to it."""

    def __init__(self, data_dir=None, config_dir=None, filename=None):
        # `None` lets libmnemosyne pick the standard per-OS location.
        self.data_dir = os.path.abspath(data_dir) if data_dir else None
        self.config_dir = os.path.abspath(config_dir) if config_dir else None
        self.filename = filename
        self.mnemosyne = None
        self.media_dir = None
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="mnemosyne-core")

    # -- lifecycle -----------------------------------------------------------

    async def start(self):
        """Boot the core *on the worker thread* so the DB connection lives
        there too."""
        await self._run_on_worker(self._initialise)

    def _initialise(self):
        if self.data_dir:
            os.makedirs(self.data_dir, exist_ok=True)
        if self.config_dir:
            os.makedirs(self.config_dir, exist_ok=True)
        mnemosyne = WebMnemosyne()
        mnemosyne.initialise(self.data_dir, config_dir=self.config_dir,
                            filename=self.filename, automatic_upgrades=True)
        self.mnemosyne = mnemosyne
        self._refresh_media_dir()

    async def stop(self):
        if self.mnemosyne is not None:
            await self._run_on_worker(self.mnemosyne.finalise)
            self.mnemosyne = None
        self._executor.shutdown(wait=True)

    # -- the only door into the core -----------------------------------------

    async def call(self, fn):
        """Run `fn(mnemosyne)` on the worker thread and await the result."""
        return await self._run_on_worker(lambda: fn(self.mnemosyne))

    async def _run_on_worker(self, fn):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, fn)

    async def switch_database(self, filename, create=False):
        """Save the current deck and open (or create) another one."""
        await self._run_on_worker(lambda: self._switch(filename, create))

    def _switch(self, filename, create):
        from mnemosyne.libmnemosyne.utils import contract_path
        m = self.mnemosyne
        db = m.database()
        if db.is_loaded():
            db.save()
        if create:
            db.new(filename)
        else:
            db.load(filename)  # falls back to new() if the file is missing
        m.config()["last_database"] = contract_path(
            db._path, m.config().data_dir)
        m.controller().update_title()
        # The card queue belongs to the previous deck; rebuild it.
        m.review_controller().reset()
        self._refresh_media_dir()

    def _refresh_media_dir(self):
        """Cache the media dir so static file serving doesn't need the lock.

        Must be called on the worker thread (after load / deck switch)."""
        try:
            self.media_dir = self.mnemosyne.database().media_dir()
        except Exception:
            self.media_dir = None
