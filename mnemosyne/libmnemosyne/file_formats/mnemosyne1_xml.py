#
# mnemosyne1_xml.py <Johannes.Baiter@gmail.com>
#

import os
import time
from xml.etree import cElementTree

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.utils import rand_uuid, MnemosyneError
from mnemosyne.libmnemosyne.file_formats.mnemosyne1 import Mnemosyne1


class Mnemosyne1XML(FileFormat, Mnemosyne1):

    description = _("Mnemosyne 1.x *.XML files")
    extension = ".xml"
    filename_filter = _("Mnemosyne 1.x XML files") + " (*.xml)"
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        Mnemosyne1.__init__(self, component_manager)
        self.anon_to_id = {}

    def do_import(self, filename, extra_tag_names=""):
        FileFormat.do_import(self, filename, extra_tag_names)
        w = self.main_widget()
        # The import process generates card log entries which have new 2.0
        # ids as opposed to their old 1.x ids, so we need to delete them
        # later.
        db = self.database()
        log_index = db.current_log_index()
        try:
            w.set_progress_text(_("Importing cards..."))
            self.read_items_from_mnemosyne1_xml(filename)
            self.create_cards_from_mnemosyne1(extra_tag_names)
        except MnemosyneError:
            w.close_progress()
            return
        db.remove_card_log_entries_since(log_index)
        # We now generate 'added card' events with the proper ids.
        timestamp = int(time.time())
        for item in self.items:
            db.log_added_card(timestamp, item.id)
        self.database().link_inverse_cards()
        w.close_progress()
        self.warned_about_missing_media = False

    def read_items_from_mnemosyne1_xml(self, filename):
        # Reset anonymiser when importing a new file, otherwise information
        # from the previous file still lingers and we get erroneously think
        # we've imported this before.
        self.anon_to_id = {}
        w = self.main_widget()
        try:
            tree = cElementTree.parse(filename)
        except cElementTree.ParseError as e:
            w.show_error(_("Unable to parse file:") + str(e))
            raise MnemosyneError
        except:
            w.show_error(_("Unable to open file."))
            raise MnemosyneError
        if tree.getroot().tag != "mnemosyne" or \
            tree.getroot().get("core_version") != "1":
            w.show_error(_
                    ("XML file does not seem to be a Mnemosyne 1.x XML file."))
            raise MnemosyneError
        self.starttime = 0
        if tree.getroot().get("time_of_start"):
            self.starttime = int(tree.getroot().get("time_of_start"))
        category_with_name = {}
        self.categories = []
        for element in tree.findall("category"):
            category = Mnemosyne1.MnemosyneCore.Category()
            category.name = element.find("name").text
            category.active = bool(element.get("active"))
            self.categories.append(category)
            category_with_name[category.name] = category
        self.items = []
        warned_about_import = False
        for element in tree.findall("item"):
            item = Mnemosyne1.MnemosyneCore.Item()
            item.id = element.get("id")
            if not item.id:
                item.id = rand_uuid()
            if item.id.startswith('_'):
                item.id = self.unanonymise_id(item.id)
            item.q = element.find("Q").text
            item.a = element.find("A").text
            if item.a is None:
                item.a = ""
            item.cat = category_with_name[element.find("cat").text]
            if element.get("gr"):
                if not warned_about_import:
                    result = w.show_question(_("This XML file contains learning data. It's best to import this from a mem file, in order to preserve historical statistics. Continue?"), _("Yes"), _("No"), "")
                    warned_about_import = True
                    if result == 1:  # No
                        return
                item.grade = int(element.get("gr"))
            else:
                item.grade = 0
            if element.get("e"):
                item.easiness = float(element.get("e"))
            else:
                item.easiness = 2.5
            if element.get("ac_rp"):
                item.acq_reps = int(element.get("ac_rp"))
            else:
                item.acq_reps = 0
            if element.get("rt_rp"):
                item.ret_reps = int(element.get("rt_rp"))
            else:
                item.ret_reps = 0
            if element.get("lps"):
                item.lapses = int(element.get("lps"))
            else:
                item.lapses = 0
            if element.get("ac_rp_l"):
                item.acq_reps_since_lapse = int(element.get("ac_rp_l"))
            else:
                item.acq_reps_since_lapse = 0
            if element.get("rt_rp_l"):
                item.ret_reps_since_lapse = int(element.get("rt_rp_l"))
            else:
                item.ret_reps_since_lapse = 0
            if element.get("l_rp"):
                item.last_rep = int(float(element.get("l_rp")))
            else:
                item.last_rep = 0
            if element.get("n_rp"):
                item.next_rep = int(float(element.get("n_rp")))
            else:
                item.next_rep = 0
            if element.get("u"):
                item.unseen = bool(element.get("u"))
            else:
                if item.acq_reps <= 1 and item.ret_reps == 0 \
                    and item.grade == 0:
                    item.unseen = True
                else:
                    item.unseen = False
            self.items.append(item)

    def unanonymise_id(self, item_id):
        if "." in item_id:
            old_id, suffix = item_id.split(".", 1)
            suffix = "." + suffix
        else:
            old_id, suffix = item_id, ""
        if old_id in self.anon_to_id:
            item_id = self.anon_to_id[old_id]
        else:
            item_id = rand_uuid()
            self.anon_to_id[old_id] = item_id
        return item_id + suffix

