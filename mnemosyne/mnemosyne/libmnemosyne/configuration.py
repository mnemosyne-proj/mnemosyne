#
# configuration.py <Peter.Bienstman@UGent.be>
#

import random
import os
import sys
import cPickle

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.exceptions import * # TODO: remove


class Configuration(Component):

    def __init__(self):
        self._config = {}
        
    def set_defaults(self):
        
        """Fill the config with default values.  Is called after every load,
        since a new version of Mnemosyne might have introduced new keys."""
        
        c = self._config
        c.setdefault("first_run", True)
        c.setdefault("path", "default.mem")
        c.setdefault("import_dir", self.basedir)
        c.setdefault("import_format", "XML")
        c.setdefault("reset_learning_data_import", False)
        c.setdefault("export_dir", self.basedir)
        c.setdefault("export_format", "XML")
        c.setdefault("reset_learning_data_export", False)
        c.setdefault("import_img_dir", self.basedir)
        c.setdefault("import_sound_dir", self.basedir)
        c.setdefault("user_id", md5(str(random.random())).hexdigest()[0:8])
        c.setdefault("upload_logs", True)
        c.setdefault("upload_server", "mnemosyne-proj.dyndns.org:80")
        c.setdefault("log_index", 1)
        c.setdefault("QA_font", None)
        c.setdefault("list_font", None)
        c.setdefault("grade_0_items_at_once", 5)
        c.setdefault("randomise_new_cards", False)
        c.setdefault("last_add_vice_versa", False)
        c.setdefault("last_add_category", "<default>")
        c.setdefault("sort_column", None)
        c.setdefault("sort_order", None)
        c.setdefault("show_intervals", "never")
        c.setdefault("only_editable_when_answer_shown", False)
        c.setdefault("locale", None)
        c.setdefault("show_daily_tips", True)
        c.setdefault("tip", 0)
        c.setdefault("backups_to_keep", 5)
        c.setdefault("day_starts_at", 3)

    def __getitem__(self, key):
        try:
            return self._config[key]
        except IndexError:
            raise KeyError

    def __setitem__(self, key, value):
        self._config[key] = value
        
    def load(self):
        try:
            config_file = file(os.path.join(self.basedir, "config"), 'rb')
            for k,v in cPickle.load(config_file).iteritems():
                self._config[k] = v
            self.set_defaults()
        except:
            raise ConfigError(stack_trace=True)

    def save(self):
        try:
            config_file = file(os.path.join(self.basedir, "config"), 'wb')
            cPickle.dump(self._config, config_file)
        except:
            raise SaveError
            
    def initialise(self, basedir=None):
        
        """Typical initialisation sequence. Custom applications can modify this
        as needed.
        
        """
        
        self.determine_basedir(basedir)
        self.fill_basedir()
        self.load()
        self.load_user_config()
        self.correct_config()

    def determine_basedir(self, basedir):
        self.old_basedir = None
        if basedir == None:
            home = os.path.expanduser("~")
            if sys.platform == "darwin":
                self.old_basedir = os.path.join(home, ".mnemosyne")
                self.basedir = os.path.join(home, "Library", "Mnemosyne")
                if not os.path.exists(self.basedir) \
                   and os.path.exists(self._old_basedir):
                    self.migrate_basedir(self.old_basedir, self.basedir)
            else:
                self.basedir = os.path.join(home, ".mnemosyne")
        else:
            self.basedir = basedir
            

    def fill_basedir(self):
        
        """ Fill basedir with configuration files. Do this even if basedir
        already exists, because we might have added new files since the
        last version.
        
        """
        
        join = os.path.join
        exists = os.path.exists
        # Create paths.
        if not exists(self.basedir):
            os.mkdir(self.basedir)
        for directory in ["history", "latex", "css", "plugins", \
                          "backups", "sessions"]:
            if not exists(join(self.basedir, directory)):
                os.mkdir(join(self.basedir, directory))
        # Create latex configuration files.
        latexdir = join(self.basedir, "latex")
        preamble = join(latexdir, "preamble")
        postamble = join(latexdir, "postamble")
        dvipng = join(latexdir, "dvipng")
        if not os.path.exists(preamble):
            f = file(preamble, 'w')
            print >> f, "\\documentclass[12pt]{article}"
            print >> f, "\\pagestyle{empty}"
            print >> f, "\\begin{document}"
            f.close()
        if not os.path.exists(postamble):
            f = file(postamble, 'w')
            print >> f, "\\end{document}"
            f.close()
        if not os.path.exists(dvipng):
            f = file(dvipng, 'w')
            print >> f, "dvipng -D 200 -T tight tmp.dvi"
            f.close()
        # Create default configuration.
        if not os.path.exists(os.path.join(self.basedir, "config")):
            self.save()
        # Create default config.py.
        configfile = os.path.join(self.basedir, "config.py")
        if not os.path.exists(configfile):
            f = file(configfile, 'w')
            print >> f, \
"""# Mnemosyne configuration file.

# Upload server. Only change when prompted by the developers.
upload_server = "mnemosyne-proj.dyndns.org:80"

# Set to True to prevent you from accidentally revealing the answer
# when clicking the edit button.
only_editable_when_answer_shown = False

# The number of daily backups to keep. Set to -1 for no limit.
backups_to_keep = 5

# The moment the new day starts. Defaults to 3 am. Could be useful to
# change if you are a night bird.
day_starts_at = 3"""
            f.close()

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
                    if var in self._config.keys():
                        self._config[var] = getattr(user_config, var)
            except:
                raise ConfigError(stack_trace=True)
                
    def correct_config(self):
        # Update paths if the location has migrated.
        if self.old_basedir:
            for key in ["import_dir", "export_dir", "import_img_dir",
                        "import_sound_dir"]:
                if _config[key] == old_basedir:
                    _config[key] = self.basedir
        # Recreate user id and log index from history folder in case the
        # config file was accidentally deleted.
        if self._config["log_index"] == 1:
            _dir = os.listdir(unicode(os.path.join(self.basedir, "history")))
            history_files = [x for x in _dir if x[-4:] == ".bz2"]
            history_files.sort()
            if history_files:
                last = history_files[-1]
                user, index = last.split('_')
                index = int(index.split('.')[0]) + 1

    def migrate_basedir(old, new):
        if os.path.islink(self, _old_basedir):
            print "Not migrating %s to %s because " % (old, new) \
                    + "it is a symlink."
            return
        # Migrate Mnemosyne basedir to new location and create a symlink from
        # the old one. The other way around is a bad idea, because a user
        # might decide to clean up the old obsolete directory, not realising
        # the new one is a symlink.
        print "Migrating %s to %s" % (old, new)
        try:
            os.rename(old, new)
        except OSError:
            print "Move failed, manual migration required."
            return
        # Now create a symlink for backwards compatibility.
        try:
            os.symlink(new, old)
        except OSError:
            print "Backwards compatibility symlink creation failed."
