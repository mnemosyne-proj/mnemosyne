#
# configuration.py <Peter.Bienstman@gmail.com>
#

import os
import re
import sys
import time
import sqlite3
import threading
import importlib
import textwrap
from locale import getdefaultlocale

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.schedulers.cramming import RANDOM
from mnemosyne.libmnemosyne.utils import rand_uuid, traceback_string

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.

re_long_int = re.compile(r"\d+L")

def config_py():
  return textwrap.dedent(
  """  # Mnemosyne configuration file.

  # This file contains settings which we deem to be too specialised to be
  # accesible from the GUI. However, if you use some of these settings, feel
  # free to inform the developers so that it can be re-evaluated if these
  # settings need to be exposed in the GUI.

  # Science server. Only change when prompted by the developers.
  science_server = "mnemosyne-proj.dyndns.org:80"

  # Set to True to prevent you from accidentally revealing the answer when
  # clicking the edit button.
  only_editable_when_answer_shown = False

  # Set to False if you don't want the tag names to be shown in the review
  # window.
  show_tags_during_review = True

  # The number of daily backups to keep. Set to -1 for no limit.
  max_backups = 10

  # Start the card browser with the last used colum sort. Could have a
  # performance penalty for large databases.
  start_card_browser_sorted = True

  # The moment the new day starts. Defaults to 3 am. Could be useful to change
  # if you are a night bird. You can only set the hours, not minutes, and
  # midnight corresponds to 0.
  day_starts_at = 3

  # On mobile clients with slow SD cards copying a large database for the backup
  # before sync can take longer than the sync itself, so we offer reckless users
  # the possibility to skip this.
  backup_before_sync = True

  # Latex preamble. Note that for the pre- and postamble you need to use double
  # slashes instead of single slashes here, to have them escaped when Python
  # reads them in.
  latex_preamble = r\"\"\"
  \documentclass[12pt]{article}
  \pagestyle{empty}
  \\begin{document}\"\"\"

  # Latex postamble.
  latex_postamble = r\"\"\"\end{document}\"\"\"

  # Latex command.
  latex = "latex -interaction=nonstopmode"

  # Latex dvipng command.
  dvipng = "dvipng -D 200 -T tight tmp.dvi"

  # Put an upper limit on the scheduled interval. Does not work retroactively, only for new reviews.
  # Should be set on each device, including mobile clients. Be careful with this setting: if you
  # accidentally set it e.g. to 1 day, you will mess up your schedule completely.
  max_scheduled_interval_days = None
  """)

class Configuration(Component, dict):

    component_type = "config"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.data_dir = None
        self.config_dir = None
        self.keys_to_sync = []
        self.server_only = False
        self.lock = threading.Lock()
        self.determine_dirs()

    def activate(self):
        Component.activate(self)
        self.fill_dirs()
        self.load()
        self.load_user_config()
        self.set_defaults()

    def set_defaults(self):

        """Fill the config with default values.  Is called after every load,
        since a new version of Mnemosyne might have introduced new keys.

        """

        for key, value in \
            list({"last_database": \
                self.database().default_name + self.database().suffix,
             "first_run": True,
             "import_img_dir": self.data_dir,
             "import_sound_dir": self.data_dir,
             "import_video_dir": self.data_dir,
             "import_flash_dir": self.data_dir,
             "import_plugin_dir": os.path.expanduser("~"),
             "user_id": None,
             "upload_science_logs": True,
             "science_server": "mnemosyne-proj.dyndns.org:80",
             "max_log_size_before_upload": 64000, # For testability.
             "show_daily_tips": True,
             "current_tip": 0,
             "font": {}, # [card_type.id][fact_key]
             "font_colour": {}, # [card_type.id][fact_key]
             "background_colour": {}, # [card_type.id]
             "alignment": {}, # [card_type.id]
             "hide_pronunciation_field": {}, # [card_type.id]
             "language_id": {}, # [card_type.id], ISO code
             "sublanguage_id": {}, # [card_type.id], ISO code
             "foreign_fact_key": {}, # [card_type.id]
             "translation_language_id": {}, # [card_type.id], ISO code
             "non_latin_font_size_increase": 0,
             "non_memorised_cards_in_hand": 10,
             "randomise_new_cards": False,
             "randomise_scheduled_cards": False,
             "cramming_store_state": True,
             "max_ret_reps_for_recent_cards": 1,
             "max_ret_reps_since_lapse": 999999, 
             "cramming_order": RANDOM,
             "show_intervals": "never",
             "only_editable_when_answer_shown": False,
             "show_tags_during_review": True,
             "ui_language": self.default_language(),
             "max_backups": 10,
             "backup_before_sync": True,
             "check_for_edited_local_media_files": False,
             "interested_in_old_reps": True,
             "single_database_help_shown": False,
             "save_database_help_shown": False,
             "find_duplicates_help_shown": False,
             "star_help_shown": False,
             "start_card_browser_sorted": False,
             "day_starts_at": 3,
             "save_after_n_reps": 10,
             "latex_preamble": "\\documentclass[12pt]{article}\n"+
                               "\\pagestyle{empty}\n\\begin{document}",
             "latex_postamble": "\\end{document}",
             "latex": "latex -interaction=nonstopmode",
             "dvipng": "dvipng -D 200 -T tight tmp.dvi",
             "active_plugins": set(), # Plugin class name, not instance.
             "media_autoplay": True,
             "media_controls": False,
             "run_sync_server": False,
             "run_web_server": False,
             "sync_server_port": 8512,
             "web_server_port": 8513,
             "remote_access_username": "",
             "remote_access_password": "",
             "remote_access_password_algo": "",
             "warned_about_learning_ahead": False,
             "shown_backlog_help": False,
             "shown_learn_new_cards_help": False,
             "shown_schedule_help": False,
             "asynchronous_database": False,
             "author_name": "",
             "author_email": "",
             "import_dir": os.path.expanduser("~"),
             "import_format": None,
             "import_extra_tag_names": "",
             "export_dir": os.path.expanduser("~"),
             "export_format": None,
             "last_db_maintenance": time.time() - 1 * DAY,
             "QA_split": "fixed", # "fixed", "adaptive", "single_window",
             "study_mode": "ScheduledForgottenNew",
             "tts_dir_for_card_type_id": {}, # card_type_id, dir
             "max_scheduled_interval_days": None
            }.items()):
            self.setdefault(key, value)
        # These keys will be shared in the sync protocol. Front-ends can
        # modify this list, e.g. if they don't want to override the fonts.
        self.keys_to_sync = ["font", "font_colour", "background_colour",
             "alignment", "non_latin_font_size_increase",
             "hide_pronunciation_field", "non_memorised_cards_in_hand",
             "randomise_new_cards", "randomise_scheduled_cards",
             "max_ret_reps_since_lapse",
             "ui_language", "day_starts_at", "latex_preamble",
             "latex_postamble", "latex", "dvipng", "max_backups",
             "language_id", "sublanguage_id", "foreign_fact_key"]
        # If the user id is not set, it's either because this is the first run
        # of the program, or because the user deleted the config file. In the
        # latter case, we try to recuperate the id from the history files.
        if self["user_id"] is None:
            _dir = os.listdir(os.path.join(self.data_dir, "history"))
            history_files = [x for x in _dir if x[-4:] == ".bz2"]
            if not history_files:
                self["user_id"] = rand_uuid()
            else:
                self["user_id"] = history_files[0].split("_", 1)[0]
        # Hash the remote access passwords if it was previously stored in plain
        # text by an older version of Mnemosyne.
        if self["remote_access_password"] != "" and \
                self["remote_access_password_algo"] == "":
            from argon2 import PasswordHasher
            from argon2.exceptions import HashingError
            try:
                ph = PasswordHasher()
                self["remote_access_password"] = \
                    ph.hash(self["remote_access_password"])
                self["remote_access_password_algo"] = "argon2"
            except HashingError:
                pass
        self["latex"] = self["latex"].strip().split()
        self["dvipng"] = self["dvipng"].strip().split()
        # Allow other plugins or frontend to set their configuration data.
        for f in self.component_manager.all("hook", "configuration_defaults"):
            f.run()
        self.save()

    def __setitem__(self, key, value):
        with self.lock:
            if key in self.keys_to_sync:
                # Don't log when reading the settings from file during startup.
                if self.log().active:
                    self.log().edited_setting(key)
            dict.__setitem__(self, key, value)

    def load(self):
        filename = os.path.join(self.config_dir, "config.db")
        # Create database tables if needed.
        with self.lock:
            con = sqlite3.connect(filename)
            is_new = (con.execute("""select 1 from sqlite_master where
                type='table' and name='config' limit 1;""").\
                      fetchone() is None)
            if is_new:
                con.executescript("""
                create table config(
                    key text primary key,
                    value text
                );""")
                con.commit()
        # Quick-and-dirty system to allow us to instantiate GUI variables
        # from the config db. The alternatives (e.g. having the frontend pass
        # along modules to import) seem to be much more verbose and quirky.
        try:
            import PyQt6
        except:
            pass
        try:
            import PyQt6.QtCore
        except:
            pass
        # Set config settings.
        for cursor in con.execute("select key, value from config"):
            # When importing Python 2 representations, strip the L
            # from long integers.
            value = re_long_int.sub(lambda x : x.group()[:-1], cursor[1])
            try:
                self[cursor[0]] = eval(value)
            except Exception as e:
                # This can fail if we are running headless now after running
                # the GUI previously.
                print(e)
        with self.lock:
            con.commit()
            con.close()

    def save(self):
        with self.lock:
            filename = os.path.join(self.config_dir, "config.db")
            con = sqlite3.connect(filename)
            # Make sure the entries exist.
            con.executemany\
                ("insert or ignore into config(key, value) values(?,?)",
                ((key, repr(value)) for key, value in self.items()))
            # Make sure they have the right data.
            con.executemany("update config set value=? where key=?",
                ((repr(value), key) for key, value in self.items()))
            con.commit()
            con.close()

    def determine_dirs(self):  # pragma: no cover
        # If the config dir was already set by the user, use that.
        if self.config_dir is not None:
            return
        # Return if data_dir was already set by the user. In that case, we
        # also store the config in that directory.
        if self.data_dir is not None:
            self.config_dir = self.data_dir
            return
        join = os.path.join
        if sys.platform == "win32":
            import ctypes
            n = ctypes.windll.kernel32.GetEnvironmentVariableW\
                ("APPDATA", None, 0)
            buf = ctypes.create_unicode_buffer("\0"*n)
            ctypes.windll.kernel32.GetEnvironmentVariableW("APPDATA", buf, n)
            self.data_dir = join(buf.value, "Mnemosyne")
            self.config_dir = self.data_dir
        elif sys.platform == "darwin":
            home = os.path.expanduser("~")
            self.data_dir = join(home, "Library", "Mnemosyne")
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
            self.data_dir = join(self.data_dir, "mnemosyne")
            if "XDG_CONFIG_HOME" in os.environ:
                self.config_dir = os.environ["XDG_CONFIG_HOME"]
            else:
                self.config_dir = join(home, ".config")
            self.config_dir = join(self.config_dir, "mnemosyne")

    def fill_dirs(self):

        """Fill data_dir and config_dir. Do this even if they already exist,
        because we might have added new files since the last version.

        """

        exists = os.path.exists
        join = os.path.join
        # Create paths.
        if not exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not exists(self.config_dir):
            os.makedirs(self.config_dir)
        for directory in ["history", "plugins", "backups"]:
            if not exists(join(self.data_dir, directory)):
                os.mkdir(join(self.data_dir, directory))
        # Create default config.py.
        config_file = join(self.config_dir, "config.py")
        if not exists(config_file):
            f = open(config_file, "w")
            print(config_py(), file=f)
            f.close()
        # Create machine_id. Do this in a separate file, as extra warning
        # signal that people should not copy this file to a different machine.
        machine_id_file = join(self.config_dir, "machine.id")
        if not exists(machine_id_file):
            f = open(machine_id_file, "w")
            print(rand_uuid(), file=f)
            f.close()

    card_type_properties_generic = ["background_colour", "alignment",
        "hide_pronunciation_field", "language_id",
        "sublanguage_id", "foreign_fact_key", "translation_language_id"]
    card_type_properties_for_fact_key = ["font", "font_colour"]
    card_type_properties = card_type_properties_generic + \
        card_type_properties_for_fact_key

    def set_card_type_property(self, property_name, property_value, card_type,
            fact_key=None):

        """Set a property (like font, colour, ..) for a certain card type.
        If fact_key is None, then this will be applied to all fact keys.

        This info is not stored in the database, but in the configuration,
        to allow different clients to have different settings, even though
        they exchange data during sync.

        """

        if property_name not in self.card_type_properties:
            raise KeyError
        # With the nested directories, we don't fall back on self.__setitem__,
        # so we have to log a event here ourselves.
        if property_name in self.keys_to_sync:
          self.log().edited_setting(property_name)
        if property_name in self.card_type_properties_generic:
            if property_value is None:
                self[property_name].pop(card_type.id, None)
            else:
                self[property_name][card_type.id] = property_value
        else:
            self[property_name].setdefault(card_type.id, {})
            for _fact_key in card_type.fact_keys():
                self[property_name][card_type.id].setdefault(_fact_key, None)
            if not fact_key:
                fact_keys = card_type.fact_keys()
            else:
                fact_keys = [fact_key]
            for _fact_key in fact_keys:
                self[property_name][card_type.id][_fact_key] = property_value

    def card_type_property(self, property_name, card_type, fact_key=None,
                            default=None):
        if property_name in self.card_type_properties_generic:
            try:
                return self[property_name][card_type.id]
            except KeyError:
                return default
        else:
            try:
                return self[property_name][card_type.id][fact_key]
            except KeyError:
                return default

    def clone_card_type_properties(self, old_card_type, new_card_type):
      for property_name in self.card_type_properties_generic:
          old_value = self.card_type_property(property_name, old_card_type)
          if old_value:
              self.set_card_type_property(\
                  property_name, old_value, new_card_type)
      for property_name in self.card_type_properties_for_fact_key:
          for fact_key in new_card_type.fact_keys():
              old_value = self.card_type_property(property_name,
                  old_card_type, fact_key)
              if old_value:
                  self.set_card_type_property(property_name, old_value, \
                      new_card_type, fact_key)

    def delete_card_type_properties(self, card_type):
        for property_name in self.card_type_properties:
            if card_type.id in self[property_name]:
                del self[property_name][card_type.id]

    def machine_id(self):
        return open(os.path.join(self.config_dir, "machine.id")).\
            readline().rstrip()

    def load_user_config(self):
        if self.config_dir not in sys.path:
            sys.path.insert(0, self.config_dir)
        config_file_c = os.path.join(self.config_dir, "config.pyc")
        if os.path.exists(config_file_c):
            os.remove(config_file_c)
        config_file = os.path.join(self.config_dir, "config.py")
        if os.path.exists(config_file):
            try:
                import config
                config = importlib.reload(config)
                for var in dir(config):
                    if var in self:
                        self[var] = getattr(config, var)
            except:
                raise RuntimeError(_("Error in config.py:") \
                          + "\n" + traceback_string())

    def change_user_id(self, new_user_id):

        """When a client syncs for the first time with a server, we need to
        set the client's user_id identical to the one of the server, in order
        for the uploaded anonymous logs to be consistent.

        """

        if new_user_id == self["user_id"]:
            return
        old_user_id = self["user_id"]
        self["user_id"] = new_user_id
        from mnemosyne.libmnemosyne.component_manager import \
             migrate_component_manager
        migrate_component_manager(old_user_id, new_user_id)
        self.save()

    def default_language(self):
        """use the OS language settings and if possible return with the
        language code like 'en', 'de', 'it', etc.  If we don't have a
        translation for the default OS language return with the default 'en'

        """
        # Use the default OS language settings is possible.
        # getdefaultlocale is OS independent and works on all platforms.
        system_language, _ = getdefaultlocale()
        # if no default locale can be found, default to English
        if system_language is None:
            system_language = 'en_us'
        lang_code = system_language.split("_")[0]

        # Special case ca@valencia, we only support this specific one.
        if "valencia" in system_language:
            return "ca@valencia"

        # Languages with multiple dialect like zh_CN, zh_TW, zh_HK, pt_BR
        # comes first.
        if system_language in self.gui_translator().supported_languages():
            return system_language
        # Languages with only 1 dialect.
        elif lang_code in self.gui_translator().supported_languages():
            default_lang = lang_code
        # Default should be english always if no better match based on the
        # default OS language.
        else:
            default_lang = "en"

        return default_lang
