"""Hatchling build hook that compiles Mnemosyne's Qt ``.ui`` files.

The PyQt6 ``.ui`` files in ``mnemosyne/pyqt_ui`` are compiled into ``ui_*.py``
modules before the package is built. This mirrors what
``mnemosyne/pyqt_ui/makefile`` does, but drives the existing ``pyuic6`` wrapper
directly so that no ``make`` is required in the (possibly isolated) build
environment. PyQt6 must be importable, which is why it is listed in
``[build-system].requires`` in ``pyproject.toml``.

This replaces the old Poetry ``poetry-build.py`` script.
"""

import os
import subprocess
import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

PYQT_UI_DIR = os.path.join("mnemosyne", "pyqt_ui")


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version, build_data):
        ui_dir = os.path.join(self.root, PYQT_UI_DIR)
        pyuic6 = os.path.join(ui_dir, "pyuic6")

        ui_files = sorted(f for f in os.listdir(ui_dir) if f.endswith(".ui"))
        if not ui_files:
            return

        for ui_file in ui_files:
            target = "ui_" + ui_file[:-len(".ui")] + ".py"
            self.app.display_info(f"Compiling {ui_file} -> {target}")
            result = subprocess.run(
                [sys.executable, pyuic6, ui_file],
                cwd=ui_dir,
                stdout=subprocess.PIPE,
                check=True,
            )
            with open(os.path.join(ui_dir, target), "wb") as f:
                f.write(result.stdout)

        # The generated files are gitignored; make sure they end up in the
        # wheel even though Hatchling defaults to VCS-tracked files only.
        build_data.setdefault("artifacts", []).append(
            f"{PYQT_UI_DIR}/ui_*.py"
        )
