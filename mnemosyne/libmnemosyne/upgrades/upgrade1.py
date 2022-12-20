#
# upgrade1.py <Peter.Bienstman@gmail.com>
#

import os
import sys

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class Upgrade1(Component):

    """Upgrade from 1.x to 2.x."""

    def run(self):  # pragma: no cover
        join = os.path.join
        exists = os.path.exists
        # Only do this upgrade once.
        if not self.database().is_empty():
            return
        # Determine old data_dir.
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            # This is where backup_old_dir put the old data dir.
            old_data_dir = join(home, "Library", "Mnemosyne_1")
        else:
            try:
                home = home.decode(locale.getdefaultlocale()[1])
            except:
                pass
            old_data_dir = join(home, ".mnemosyne")
        # We split off the rest to a separate function for testability.
        config_file = join(old_data_dir, "config")
        if exists(old_data_dir) and exists(config_file) and not exists(\
            join(old_data_dir, "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2")):
            self.upgrade_from_old_data_dir(old_data_dir)

    def backup_old_dir(self):  # pragma: no cover
        join = os.path.join
        # We only do this on OSX, since on the other platforms, we use a
        # different directory anyway.
        if sys.platform == "darwin":
            home = os.path.expanduser("~")
            old_data_dir = join(home, "Library", "Mnemosyne")
            backup_dir = join(home, "Library", "Mnemosyne_1")
            # Work around os.path.exists seeming to give wrong results on
            # OSX 10.6 (but not 10.7).
            if os.path.exists(join(old_data_dir, "default.db")):
                # Data was already backed up.
                return
            if os.path.exists(old_data_dir):
                if not os.path.exists(backup_dir):
                    old_files = sorted(os.listdir(old_data_dir))
                    import shutil  # Crashes on some Android machines at top level.
                    shutil.move(old_data_dir, backup_dir)
                    new_files = sorted(os.listdir(backup_dir))
                    assert old_files == new_files
                    self.main_widget().show_information(\
                _("Your old 1.x files are now stored here:\n\n" + backup_dir))
                else:
                    self.main_widget().show_error(\
_("Tried to backup your old 1.x files to %s, but that directory already exists.") \
                    % (backup_dir,))
                    sys.exit()

    def upgrade_from_old_data_dir(self, old_data_dir):
        join = os.path.join
        # Warn people that this directory is no longer used.
        open(join(old_data_dir,
            "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2"), "w").close()
        # Read old configuration.
        old_config = {}
        config_file = open(join(old_data_dir, "config"), "rb")
        import pickle
        for key, value in pickle.load(config_file).items():
            old_config[key] = value
        # Migrate configuration settings.
        if "user_id" in old_config:
            self.config()["user_id"] = old_config["user_id"]
        if "upload_logs" in old_config:
            self.config()["upload_science_logs"] = old_config["upload_logs"]
        if "non_latin_font_size_increase" in old_config:
            self.config()["non_latin_font_size_increase"] \
            = old_config["non_latin_font_size_increase"]
        for card_type in self.card_types():
            if "QA_font" in old_config:
                self.config().set_card_type_property("font",
                old_config["QA_font"], card_type)
        if "left_align" in old_config and old_config["left_align"]:
            for card_type in self.card_types():
                self.config().set_card_type_property("alignment",
                    "left", card_type)
        # Migrate latex settings.
        setting_for_file = {"dvipng": "dvipng",
                            "preamble": "latex_preamble",
                            "postamble": "latex_postamble"}
        for filename, setting in setting_for_file.items():
            full_filename = join(old_data_dir, "latex", filename)
            self.config()[setting] = ""
            if os.path.exists(full_filename):
                for line in open(full_filename):
                    self.config()[setting] += line
        # Copy over everything that does not interfere with Mnemosyne 2.
        new_data_dir = self.config().data_dir
        new_media_dir = self.database().media_dir()
        import shutil
        shutil.rmtree(join(new_data_dir, "history"))
        names = [name for name in os.listdir(old_data_dir) if name not in
            ["backups", "config", "config.py", "config.pyc",
            "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2", "error_log.txt",
            "latex", "plugins", "log.txt", "history"] \
            and not name.endswith(".mem") and not name is None]
        self.main_widget().set_progress_text(_("Copying files from 1.x..."))
        # By copying over the history folder and log.txt, we also completely
        # preserve the state of all the files that need to uploaded to the
        # science server.
        self.main_widget().set_progress_range(len(names) + 2)
        if os.path.exists(join(old_data_dir, "history")):
            shutil.copytree(join(old_data_dir, "history"),
                            join(new_data_dir, "history"))
        self.main_widget().increase_progress(1)
        shutil.copyfile(join(old_data_dir, "log.txt"),
                        join(new_data_dir, "log.txt"))
        self.main_widget().increase_progress(1)
        # We copy all the other files to the media directory. In this way,
        # if there are media files that are not explicitly referenced in the
        # cards, it will be easier for the user to fix his path errors after
        # the upgrade.
        for name in names:
            if os.path.isdir(join(old_data_dir, name)):
                try:
                    shutil.copytree(join(old_data_dir, name),
                                    join(new_media_dir, name))
                except OSError as e:
                    # https://bugs.launchpad.net/mnemosyne-proj/+bug/1210435
                    import errno
                    if e.errno != errno.EEXIST:
                        raise e
                    self.main_widget().show_information(\
                        "Skipping copying of %s because it already exists.") \
                        % (name, )
            else:
                shutil.copyfile(join(old_data_dir, name),
                                join(new_media_dir, name))
            self.main_widget().increase_progress(1)
        # Upgrade database.
        old_database = expand_path("default.mem", old_data_dir)
        for format in self.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                format.do_import(old_database)
                self.controller().reset_study_mode()
        # Give info to the user.
        info = _("Upgrade from Mnemosyne 1.x complete!") + "\n\n"
        info += _("Mnemosyne 2.x now stores its data here:") + "\n\n"
        info += self.config().data_dir + "\n"
        if self.config().config_dir != \
            self.config().data_dir: # pragma: no cover
            # Only happens on Linux, outside of the test suite.
            info += self.config().config_dir
        self.main_widget().show_information(info)
