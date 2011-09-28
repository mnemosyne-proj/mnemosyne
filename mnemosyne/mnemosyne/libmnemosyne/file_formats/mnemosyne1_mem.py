#
# mnemosyne1_mem.py <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import time
import cPickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne1 import Mnemosyne1
from mnemosyne.libmnemosyne.file_formats.science_log_parser \
     import ScienceLogParser
        
re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)
re_sound = re.compile(r"""<sound src=\".+?\">""", re.DOTALL | re.IGNORECASE)


class Mnemosyne1Mem(FileFormat, Mnemosyne1):
    
    description = _("Mnemosyne 1.x *.mem files")
    filename_filter = _("Mnemosyne 1.x *.mem databases") + " (*.mem)"
    import_possible = True
    export_possible = False

    def do_import(self, filename, extra_tag_name=None):
        self.import_dir = os.path.dirname(os.path.abspath(filename))
        self.warned_about_missing_media = False
        w = self.main_widget()
        w.set_progress_text(_("Importing cards..."))
        db = self.database()
        # Manage database indexes.
        db.before_mem_import()
        # The import process generates card log entries, which we will delete
        # in favour of those events that are recorded in the logs and which
        # capture the true timestamps. They also have new 2.0 ids, as opposed
        # to their old 1.x ids.
        log_index = db.current_log_index()
        try:
            self.read_items_from_mnemosyne1_mem(filename)
            self.create_cards_from_mnemosyne1(extra_tag_name)
        except MnemosyneError:
            w.close_progress()
            return
        db.remove_card_log_entries_since(log_index)
        # The events that we import from the science logs obviously should not
        # be reexported to these logs (this is true for both the archived logs
        # and log.txt). So, before the import, we flush the SQL logs to the
        # science logs, and after the import we edit the partership index to
        # skip these entries.
        db.dump_to_science_log()
        self.import_logs(filename)
        db.skip_science_log()
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
        # Manage database indexes.
        db.after_mem_import()
        # Detect inverses.        
        db.link_inverse_cards()
        w.close_progress()
            
    def read_items_from_mnemosyne1_mem(self, filename):
        sys.modules["mnemosyne.core"] = object()       
        sys.modules["mnemosyne.core.mnemosyne_core"] \
            = Mnemosyne1.MnemosyneCore()
        try:
            memfile = file(filename, "rb")
            header = memfile.readline()
            self.starttime, self.categories, self.items \
                = cPickle.load(memfile)
            self.starttime = self.starttime.time
        except:
            self.main_widget().show_error(_("Unable to open file."))
            raise MnemosyneError

    def import_logs(self, filename):
        w = self.main_widget()
        w.set_progress_text(_("Importing history..."))
        parser = ScienceLogParser(self.database(),
            ids_to_parse=self.items_by_id)
        log_dir = os.path.join(os.path.dirname(filename), "history")
        if not os.path.exists(log_dir):
            w.close_progress()
            w.show_information(_("No history found to import."))
            return
        filenames = [os.path.join(log_dir, logname) for logname in \
            sorted(os.listdir(unicode(log_dir))) if logname.endswith(".bz2")]       
        # log.txt can also contain data we need to import, especially on the
        # initial upgrade from 1.x. 'ids_to_parse' will make sure we only pick
        # up the relevant events. (If we do the importing after having used
        # 2.x for a while, there could be duplicate load events, etc, but these
        # don't matter.)
        filenames.append(os.path.join(os.path.dirname(filename), "log.txt"))
        w.set_progress_range(0, len(filenames))
        ignored_files = []
        for count, filename in enumerate(filenames):
            w.set_progress_value(count)
            try:
                parser.parse(filename)
            except:
                ignored_files.append(filename)
        if ignored_files:
            w.show_information(_("Ignoring unparsable files:<br/>") +\
                '<br/>'.join(ignored_files))
        w.close_progress()
