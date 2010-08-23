#
# upgrade1.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil
import cPickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class Upgrade1(Component):

    """Upgrade from 1.x to 2.x."""

    def run(self):
        join = os.path.join
        # Only do this upgrade once.
        if not self.database().is_empty():
            return
        # Determine old data_dir.
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            old_data_dir = join(unicode(home), "Library", "Mnemosyne")
        else:
            try:
                home = home.decode(locale.getdefaultlocale()[1])
            except:
                pass
            old_data_dir = join(home, ".mnemosyne")
        # We split off the rest to a separate function for testability.
        if os.path.exists(old_data_dir):
            self.upgrade_from_old_data_dir(old_data_dir)

    def upgrade_from_old_data_dir(self, old_data_dir):
        join = os.path.join
        # Warn people that this directory is no longer used.
        file(join(old_data_dir,
            "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2"), "w").close()
        # Read old configuration.
        old_config = {}
        config_file = file(join(old_data_dir, "config"), "rb")
        for key, value in cPickle.load(config_file).iteritems():
            old_config[key] = value
        # Migrate configuration settings.
        self.config()["user_id"] = old_config["user_id"]
        self.config()["log_index"] = old_config["log_index"]
        self.config()["upload_science_logs"] = old_config["upload_logs"]
        for card_type in self.card_types():
            card_type.renderer().set_property("font", old_config["QA_font"],
                card_type)
        if old_config["left_align"]:
            for card_type in self.card_types():                
                card_type.renderer().set_property(\
                    "alignment", "left", card_type)
        # Migrate latex settings.
        setting_for_file = {"dvipng": "dvipng",
                            "preamble": "latex_preamble",
                            "postamble": "latex_postamble"}
        for filename, setting in setting_for_file.iteritems():
            full_filename = join(old_data_dir, "latex", filename)
            self.config()[setting] = ""
            for line in file(full_filename):
                self.config()[setting] += line
        # Copy over the history folder and log.txt. In this way, we also
        # completely preserve the state of all the files that need to uploaded
        # to the science server.
        new_data_dir = self.config().data_dir
        shutil.rmtree(join(new_data_dir, "history"))
        shutil.copytree(join(old_data_dir, "history"),
                        join(new_data_dir, "history"))
        shutil.copyfile(join(old_data_dir, "log.txt"),
                        join(new_data_dir, "log.txt"))
        # Upgrade database.
        old_database = expand_path(old_config["path"], old_data_dir)
        for format in self.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                format.do_import(old_database)
                self.review_controller().reset()
        # Give info to the user.
        info = _("Upgrade from Mnemosyne 1.x complete!") + "\n\n"
        info += _("Mnemosyne 2.x now stores its data here:") + "\n\n"
        info += self.config().data_dir + "\n"
        if self.config().config_dir != self.config().data_dir:
            info += self.config().config_dir
        self.main_widget().information_box(info)
