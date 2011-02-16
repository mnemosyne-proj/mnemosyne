#
# configuration.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import locale
import cPickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import rand_uuid, traceback_string

config_py = \
"""# Mnemosyne configuration file.

# Science server. Only change when prompted by the developers.
science_server = "mnemosyne-proj.dyndns.org:80"

# Set to True to prevent you from accidentally revealing the answer
# when clicking the edit button.
only_editable_when_answer_shown = False

# The number of daily backups to keep. Set to -1 for no limit.
backups_to_keep = 5

# The moment the new day starts. Defaults to 3 am. Could be useful to
# change if you are a night bird. You can only set the hours, not
# minutes, and midnight corresponds to 0.
day_starts_at = 3

# The number of repetitions that need to happen before autosave.
# Setting this to 1 means saving after every repetition.
save_after_n_reps = 1

# Latex preamble. Note that for the pre- and postamble you need to
# use double slashes instead of single slashes here, to have them
# escaped when Python reads them in.
latex_preamble = \"\"\"\\\\documentclass[12pt]{article}
\\\\pagestyle{empty}
\\\\begin{document}\"\"\"

# Latex postamble.
latex_postamble = "\\\\end{document}"

# Latex command.
latex = "latex -interaction=nonstopmode"

# Latex dvipng command.
dvipng = "dvipng -D 200 -T tight tmp.dvi"
"""

class Configuration(Component, dict):

    component_type = "config"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.data_dir = None
        self.config_dir = None

    def activate(self):
        self.determine_dirs()
        self.fill_dirs()
        self.load()
        self.load_user_config()
        self.correct_config()

    def set_defaults(self):

        """Fill the config with default values.  Is called after every load,
        since a new version of Mnemosyne might have introduced new keys.

        """

        for key, value in \
            {"first_run": True,
             "path": self.database().default_name + self.database().suffix,
             "import_dir": self.data_dir,
             "import_format": "XML",
             "reset_learning_data_import": False,
             "export_dir": self.data_dir,
             "export_format": "XML",
             "reset_learning_data_export": False,
             "import_img_dir": self.data_dir,
             "import_sound_dir": self.data_dir,
             "import_video_dir": self.data_dir,
             "user_id": None,
             "upload_science_logs": True,
             "science_server": "mnemosyne-proj.dyndns.org:80",
             "log_index": 1,
             "font": {}, # [card_type.id][fact_key]
             "font_colour": {}, # [card_type.id][fact_key]
             "background_colour": {}, # [card_type.id]
             "alignment": {}, # [card_type.id]
             "non_memorised_cards_in_hand": 10,
             "randomise_new_cards": False,
             "randomise_scheduled_cards": False,
             "memorise_sister_cards_on_same_day": False,
             "show_intervals": "never",
             "only_editable_when_answer_shown": False,
             "ui_language": None,
             "show_daily_tips": True,
             "tip": 0,
             "backups_to_keep": 10,
             "day_starts_at": 3,
             "save_after_n_reps": 1,
             "latex_preamble": "\\documentclass[12pt]{article}\n"+
                              "\\pagestyle{empty}\n\\begin{document}",
             "latex_postamble": "\\end{document}",
             "latex": "latex -interaction=nonstopmode",
             "dvipng": "dvipng -D 200 -T tight tmp.dvi",
             "active_plugins": set(), # Plugin classes, not instances.
             "media_autoplay": True,
             "media_controls": False,
             "run_sync_server": False,
             "sync_server_port": 8512,
             "sync_server_username": "",
             "sync_server_password": ""
            }.items():
            self.setdefault(key, value)
        if not self["user_id"]:
            self["user_id"] = rand_uuid()
        # Allow other plugins or frontend to set their configuration data.
        for f in self.component_manager.all("hook",
            "configuration_defaults"):
            f.run()

    def load(self):
        try:
            config_file = file(os.path.join(self.config_dir, "config"), 'rb')
            for key, value in cPickle.load(config_file).iteritems():
                self[key] = value
            self.set_defaults()
        except:
            from mnemosyne.libmnemosyne.utils import traceback_string
            raise RuntimeError, _("Error in config:") \
                  + "\n" + traceback_string()
        
    def save(self):
        try:
            config_file = file(os.path.join(self.config_dir, "config"), 'wb')
            cPickle.dump(dict(self), config_file)
        except:
            from mnemosyne.libmnemosyne.utils import traceback_string
            raise RuntimeError, _("Unable to save config file:") \
                  + "\n" + traceback_string()

    def determine_dirs(self):  # pragma: no cover
        # Return if data_dir was already set by the user. In that case, we
        # also store the config in that directory.
        if self.data_dir is not None:
            self.config_dir = self.data_dir
            return
        join = os.path.join
        if sys.platform == "win32":
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW(\
                "APPDATA", None, 0)
            buf = ctypes.create_unicode_buffer(u'\0'*n)
            ctypes.windll.kernel32.GetEnvironmentVariableW(name, buf, n)
            self.data_dir = join(buf.value, "Mnemosyne2")
            self.config_dir = self.data_dir
        elif sys.platform == "darwin":
            home = os.path.expanduser("~")
            self.data_dir = join(home, "Library", "Mnemosyne2")
            self.config_dir = self.data_dir
        else:
            # Follow the freedesktop standards:
            # http://standards.freedesktop.org/basedir-spec/
            # basedir-spec-latest.html
            home = os.path.expanduser("~")
            if "XDG_DATA_HOME" in os.environ:
                self.data_dir = os.environ["XDG_DATA_HOME"]
            else:
                self.data_dir = join(home, ".local", "share")
            self.data_dir = join(self.data_dir, "mnemosyne2")
            if "XDG_CONFIG_HOME" in os.environ:
                self.config_dir = os.environ["XDG_CONFIG_HOME"]
            else:
                self.config_dir = join(home, ".config")
            self.config_dir = join(self.config_dir, "mnemosyne2")

    def fill_dirs(self):

        """Fill data_dir and config_dir. Do this even if they already exist,
        because we might have added new files since the last version.

        """

        exists = os.path.exists
        join = os.path.join
        # Create paths.
        if not exists(self.data_dir):
            os.mkdir(self.data_dir)
        if not exists(self.config_dir):
            os.mkdir(self.config_dir)
        for directory in ["history", "plugins", "backups"]:
            if not exists(join(self.data_dir, directory)):
                os.mkdir(join(self.data_dir, directory))
        # Create default configuration.
        if not exists(join(self.config_dir, "config")):
            self.save()
        # Create default config.py.
        config_file = join(self.config_dir, "config.py")
        if not exists(config_file):
            f = file(config_file, "w")
            print >> f, config_py
            f.close()
        # Create machine_id. Do this in a separate file, as extra warning
        # signal that people should not copy this file to a different machine.
        machine_id_file = join(self.config_dir, "machine.id")
        if not exists(machine_id_file):
            f = file(machine_id_file, "w")
            print >> f, rand_uuid()
            f.close()


    def set_appearance_property(self, property_name, property, card_type,
            fact_key=None):

        """Set a property (like font, colour, ..) for a certain card type.
        If fact_key is None, then this will be applied to all fact keys.

        """

        if property_name not in ["background_colour", "font", "font_colour",
                                 "alignment"]:
            raise KeyError
        if property_name == "background_colour" or \
               property_name == "alignment":
            self[property_name][card_type.id] = property
            return
        self[property_name].setdefault(card_type.id, {})
        for key in card_type.keys():
            self[property_name][card_type.id].setdefault(key, None)
        if not fact_key:
            keys = card_type.keys()
        else:
            keys = [fact_key]
        for key in keys:
            self[property_name][card_type.id][key] = property

    def machine_id(self):
        return file(os.path.join(self.config_dir, "machine.id")).\
            readline().rstrip()

    def load_user_config(self):
        sys.path.insert(0, self.config_dir)
        config_file_c = os.path.join(self.config_dir, "config.pyc")
        if os.path.exists(config_file_c):
            os.remove(config_file_c)
        config_file = os.path.join(self.config_dir, "config.py")
        if os.path.exists(config_file):
            try:
                import config as user_config
                for var in dir(user_config):
                    if var in self:
                        self[var] = getattr(user_config, var)
            except:
                # Work around the unexplained fact that config.py cannot get
                # imported right after it has been created.
                if self["first_run"] == True:
                    pass
                else:
                    raise RuntimeError, _("Error in config.py:") \
                          + "\n" + traceback_string()

    def correct_config(self):
        # Recreate user id and log index from history folder in case the
        # config file was accidentally deleted.
        if self["log_index"] == 1:
            join = os.path.join
            _dir = os.listdir(unicode(join(self.data_dir, "history")))
            history_files = [x for x in _dir if x[-4:] == ".bz2"]
            history_files.sort()
            if history_files:
                last = history_files[-1]
                user_id, log_index = last.rsplit('_', 1)
                log_index = int(log_index.split('.')[0]) + 1
                self["user_id"] = user_id
                self["log_index"] = log_index

    def change_user_id(self, new_user_id):

        """When a client syncs for the first time with a server, we need to
        set the client's user_id identical to the one of the server, in order
        for the uploaded anonymous logs to be consistent. However, we should only
        do this on a 'virgin' client.

        """

        if new_user_id == self["user_id"]:
            return
        db = self.database()
        if self["log_index"] > 1 or not db.is_empty():
            raise RuntimeError, "Unable to change user id."
        old_user_id = self["user_id"]
        self["user_id"] = new_user_id
        from mnemosyne.libmnemosyne.component_manager import \
             migrate_component_manager
        migrate_component_manager(old_user_id, new_user_id)