
#
# mnemosyne1_mem.py <Peter.Bienstman@gmail.com>
#

import os
import re
import sys
import time
import pickle

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne1 import Mnemosyne1
from mnemosyne.libmnemosyne.file_formats.science_log_parser \
     import ScienceLogParser


class Mnemosyne1Mem(FileFormat, Mnemosyne1):

    description = _("Mnemosyne 1.x *.mem files")
    extension = ".mem"
    filename_filter = _("Mnemosyne 1.x *.mem databases (*.mem)")
    import_possible = True
    export_possible = False

    def do_import(self, filename, extra_tag_names=""):
        FileFormat.do_import(self, filename, extra_tag_names)
        w = self.main_widget()
        w.set_progress_text(_("Importing cards..."))
        db = self.database()
        # The import process generates card log entries, which we will delete
        # in favour of those events that are recorded in the logs and which
        # capture the true timestamps. They also have new 2.0 ids, as opposed
        # to their old 1.x ids.
        log_index = db.current_log_index()
        try:
            self.read_items_from_mnemosyne1_mem(filename)
            self.create_cards_from_mnemosyne1(extra_tag_names)
        except MnemosyneError:
            w.close_progress()
            return
        db.remove_card_log_entries_since(log_index)
        self.import_logs(filename)
        # Force an ADDED_CARD log entry for those cards that did not figure in
        # the txt logs, e.g. due to missing or corrupt logs.
        db.add_missing_added_card_log_entries(
            set(item.id for item in self.items))
        # In 2.x, repetition events are used to update a card's last_rep and
        # next_rep during sync. In 1.x, there was no such information, and
        # calculating it from the logs will fail if they are incomplete.
        # Therefore, we force a card edit event for all cards.
        timestamp = int(time.time())
        for item in self.items:
            db.log_edited_card(timestamp, item.id)
        # Detect inverses.
        db.link_inverse_cards()
        w.close_progress()
        self.warned_about_missing_media = False

    def read_items_from_mnemosyne1_mem(self, filename):
        sys.modules["mnemosyne.core"] = object()
        sys.modules["mnemosyne.core.mnemosyne_core"] \
            = Mnemosyne1.MnemosyneCore()
        # For importing Python 2 pickles, we run into this bug:
        # http://bugs.python.org/issue22005
        # Workaround is opening this file using 'bytes' encoding, but
        # this requires extra work for us in setting up the data members.
        try:
            memfile = open(filename, "rb")
            header = memfile.readline()
            self.starttime, self.categories, self.items \
                = pickle.load(memfile, encoding="bytes")
            self.starttime = self.starttime.__dict__[b"time"]
            for category in self.categories:
                category.name = category.__dict__[b"name"]
                category.active = category.__dict__[b"active"]
                del category.__dict__[b"name"]
                del category.__dict__[b"active"]
            for item in self.items:
                if type(item.__dict__[b"id"]) == bytes:
                    item.id = str(item.__dict__[b"id"], "utf-8")
                else:
                    item.id = item.__dict__[b"id"]
                item.cat = item.__dict__[b"cat"]
                item.q = item.__dict__[b"q"]
                item.a = item.__dict__[b"a"]
                item.unseen = item.__dict__[b"unseen"]
                item.grade = item.__dict__[b"grade"]
                item.next_rep = item.__dict__[b"next_rep"]
                item.last_rep = item.__dict__[b"last_rep"]
                item.easiness = item.__dict__[b"easiness"]
                item.acq_reps = item.__dict__[b"acq_reps"]
                item.ret_reps = item.__dict__[b"ret_reps"]
                item.lapses = item.__dict__[b"lapses"]
                item.acq_reps_since_lapse = \
                    item.__dict__[b"acq_reps_since_lapse"]
                item.ret_reps_since_lapse = \
                    item.__dict__[b"ret_reps_since_lapse"]
                del item.__dict__[b"id"]
                del item.__dict__[b"cat"]
                del item.__dict__[b"q"]
                del item.__dict__[b"a"]
                del item.__dict__[b"unseen"]
                del item.__dict__[b"grade"]
                del item.__dict__[b"next_rep"]
                del item.__dict__[b"last_rep"]
                del item.__dict__[b"easiness"]
                del item.__dict__[b"acq_reps"]
                del item.__dict__[b"ret_reps"]
                del item.__dict__[b"lapses"]
                del item.__dict__[b"acq_reps_since_lapse"]
                del item.__dict__[b"ret_reps_since_lapse"]
        except (FileNotFoundError, PermissionError) as e:
            self.main_widget().show_error(_("Unable to open file."))
            raise MnemosyneError
        except Exception as e:
            import traceback
            self.main_widget().show_error(traceback.format_exc())
            raise MnemosyneError

    def import_logs(self, filename):
        w = self.main_widget()
        db = self.database()
        w.set_progress_text(_("Importing history..."))
        log_dir = os.path.join(os.path.dirname(filename), "history")
        if not os.path.exists(log_dir):
            w.close_progress()
            w.show_information(_("No history found to import."))
            return
        # The events that we import from the science logs obviously should not
        # be reexported to these logs (this is true for both the archived logs
        # and log.txt). So, before the import, we flush the SQL logs to the
        # science logs, and after the import we edit the partership index to
        # skip these entries.
        db.dump_to_science_log()
        # Manage database indexes.
        db.before_1x_log_import()
        filenames = [os.path.join(log_dir, logname) for logname in \
            sorted(os.listdir(log_dir)) if logname.endswith(".bz2")]
        # log.txt can also contain data we need to import, especially on the
        # initial upgrade from 1.x. 'ids_to_parse' will make sure we only pick
        # up the relevant events. (If we do the importing after having used
        # 2.x for a while, there could be duplicate load events, etc, but these
        # don't matter.)
        filenames.append(os.path.join(os.path.dirname(filename), "log.txt"))
        w.set_progress_range(len(filenames))
        ignored_files = []
        parser = ScienceLogParser(self.database(),
            ids_to_parse=self.items_by_id,
            machine_id=self.config().machine_id())
        for filename in filenames:
            try:
                parser.parse(filename)
            except:
                ignored_files.append(filename)
            w.increase_progress(1)
        if ignored_files:
            w.show_information(_("Ignoring unparsable files:<br/>") +\
                '<br/>'.join(ignored_files))
        # Manage database indexes.
        db.after_1x_log_import()
        db.skip_science_log()
