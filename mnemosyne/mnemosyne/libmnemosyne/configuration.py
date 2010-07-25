#
# configuration.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import locale
import cPickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string

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
        basedir = None
        resource_limited = False

    def activate(self):
        self.determine_basedir()
        self.fill_basedir()
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
             "import_dir": self.basedir, 
             "import_format": "XML",
             "reset_learning_data_import": False,
             "export_dir": self.basedir,
             "export_format": "XML", 
             "reset_learning_data_export": False,
             "import_img_dir": self.basedir, 
             "import_sound_dir": self.basedir,
             "import_video_dir": self.basedir,
             "user_id": None,
             "upload_science_logs": False, 
             "science_server": "mnemosyne-proj.dyndns.org:80",
             "log_index": 1, 
             "font": {}, # [card_type.id][fact_key]
             "background_colour": {}, # [card_type.id]             
             "font_colour": {}, # [card_type.id][fact_key]
             "alignment": {}, # [card_type.id]
             "grade_0_cards_in_hand": 10,
             "randomise_new_cards": False,
             "randomise_scheduled_cards": False,
             "memorise_related_cards_on_same_day": False, 
             "show_intervals": "never",
             "only_editable_when_answer_shown": False,
             "language": None,
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
             "sync_server_port": 9021,
             "sync_server_username": "",
             "sync_server_password": ""
            }.items():
            self.setdefault(key, value)

        if not self["user_id"]:
            import uuid
            self["user_id"] = str(uuid.uuid4())

        # Allow other plugins or frontend to set their configuration data.
        for f in self.component_manager.get_all("hook",
                                                "configuration_defaults"):
            f.run()

    def load(self):
        try:
            config_file = file(os.path.join(self.basedir,
                                            "config"), 'rb')
            for key, value in cPickle.load(config_file).iteritems():
                self[key] = value
            self.set_defaults()
        except:
            from mnemosyne.libmnemosyne.utils import traceback_string
            raise RuntimeError, _("Error in config:") \
                  + "\n" + traceback_string()
        
    def save(self):
        try:
            config_file = file(os.path.join(self.basedir,
                                            "config"), 'wb')
            cPickle.dump(dict(self), config_file)
        except:
            from mnemosyne.libmnemosyne.utils import traceback_string
            raise RuntimeError, _("Unable to save config file:") \
                  + "\n" + traceback_string()

    def determine_basedir(self):
        exists = os.path.exists
        join = os.path.join        
        self.old_basedir = None
        if self.basedir == None:
            home = os.path.expanduser("~")
            try:
                home = home.decode(locale.getdefaultlocale()[1])
            except:
                pass
            if sys.platform == "darwin":
                self.basedir = join(home, "Library", "Mnemosyne")
            else:
                self.basedir = join(home, ".mnemosyne")

    def fill_basedir(self):
        
        """ Fill basedir with configuration files. Do this even if basedir
        already exists, because we might have added new files since the
        last version.
        
        """

        exists = os.path.exists
        join = os.path.join        
        # Create paths.
        if not exists(self.basedir):
            os.mkdir(self.basedir)
        for directory in ["history", "css", "plugins", "backups"]:
            if not exists(join(self.basedir, directory)):
                os.mkdir(join(self.basedir, directory))
        # Create default configuration.
        if not exists(join(self.basedir, "config")):
            self.save()
        # Create default config.py.
        configfile = join(self.basedir, "config.py")
        if not exists(configfile):
            f = file(configfile, "w")
            print >> f, config_py
            f.close()
        # Create machine_id. Do this in a separate file, so that people can
        # copy their other config files over to a different machine without
        # problems.
        machine_id_file = join(self.basedir, "machine.id")
        if not exists(machine_id_file):
            import uuid
            f = file(machine_id_file, "w")
            print >> f, str(uuid.uuid4())
            f.close()

    def machine_id(self):
        return file(os.path.join(self.basedir, "machine.id")).\
            readline().rstrip()

    def load_user_config(self):
        sys.path.insert(0, self.basedir)
        config_file_c = os.path.join(self.basedir, "config.pyc")
        if os.path.exists(config_file_c):
            os.remove(config_file_c)
        config_file = os.path.join(self.basedir, "config.py")
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
        # Update paths if the location has migrated.
        if self.old_basedir:
            for key in ["import_dir", "export_dir", "import_img_dir",
                        "import_sound_dir"]:
                if self[key] == self.old_basedir:
                    self[key] = self.basedir
        # Recreate user id and log index from history folder in case the
        # config file was accidentally deleted.
        if self["log_index"] == 1:
            join = os.path.join
            _dir = os.listdir(unicode(join(self.basedir, "history")))
            history_files = [x for x in _dir if x[-4:] == ".bz2"]
            history_files.sort()
            if history_files:
                last = history_files[-1]
                user, index = last.rsplit('_', 1)
                index = int(index.split('.')[0]) + 1

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
