#
# upgrade1.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import cPickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class Upgrade1(Component):

    """Upgrade from 1.x to 2.0."""

    def run(self):
        # Only do this upgrade once.
        if not self.database().is_empty():
            return
        # Determine old data_dir.
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            old_data_dir = os.path.join(unicode(home), "Library", "Mnemosyne")
        else:
            try:
                home = home.decode(locale.getdefaultlocale()[1])
            except:
                pass
            old_data_dir = os.path.join(home, ".mnemosyne")
        # Warn people that this directory is no longer used.
        warning_file = file("DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2", "w")
        warning_file.close()
        # Read old configuration.
        old_config = {}
        config_file = file(os.path.join(old_data_dir, "config"), "rb")
        for key, value in cPickle.load(config_file).iteritems():
            old_config[key] = value
        # Migrate configuration settings.
        for card_type in self.card_types():
            card_type.renderer().set_property("font", old_config["QA_font"],
                card_type)
        if old_config["left_align"]:
            for card_type in self.card_types():                
                card_type.renderer().set_property(\
                    "alignment", "left", card_type)
        self.config()["upload_science_logs"] = old_config["upload_logs"]
        # Migrate latex settings.
        setting_for_file = {"dvipng": "dvipng",
                            "preamble": "latex_preamble",
                            "postamble": "latex_postamble"}
        for filename, setting in setting_for_file.iteritems():
            full_filename = os.path.join(old_data_dir, "latex", filename)
            self.config()[setting] = ""
            for line in file(full_filename):
                self.config()[setting] += line
        # Copy over the history folder and log.txt (others needed?)
        # only copy those that were uploaded.

        # Upgrade database.

        # TODO: add controller stuff
        #self.review_controller().reset()
        old_database = expand_path(old_config["path"], old_data_dir)
        for format in self.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                format.do_import(old_database)
                self.review_controller().reset()
        # Give info to user.
        info = _("Upgrade from Mnemosyne 1.x complete!") + "\n\n"
        info += _("Mnemosyne 2.x now stores its data here:") + "\n\n"
        info += self.config().data_dir + "\n"
        if self.config().config_dir != self.config().data_dir:
            info += self.config().config_dir
        self.main_widget().information_box(info)
