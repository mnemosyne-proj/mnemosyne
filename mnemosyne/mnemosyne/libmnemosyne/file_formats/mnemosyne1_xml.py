#
# mnemosyne1_xml.py <Johannes.Baiter@gmail.com>
#

import os
import time
from xml.etree import cElementTree

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne1 import Mnemosyne1


class Mnemosyne1XML(FileFormat, Mnemosyne1):

    description = _("Mnemosyne 1.x *.XML files")
    filename_filter = _("Mnemosyne 1.x XML files") + " (*.xml)"
    import_possible = True
    export_possible = False

    def do_import(self, filename, tag_name=None):
        self.import_dir = os.path.dirname(os.path.abspath(filename))
        self.warned_about_missing_media = False
        w = self.main_widget()
        try:
            w.set_progress_text(_("Importing cards..."))
            self.read_items_from_mnemosyne1_xml(filename)
            self.create_cards_from_mnemosyne1(tag_name)
        except MnemosyneError:
            w.close_progress()
            return
        self.database().link_inverse_cards()
            
    def read_items_from_mnemosyne1_xml(self, filename):
        w = self.main_widget()
        try:
            tree = cElementTree.parse(filename)
        except:
            w.show_error(_("Unable to open file."))
            raise MnemosyneError
        if tree.getroot().tag != "mnemosyne" or \
            tree.getroot().get("core_version") != "1":
            w.show_error(_
                    ("XML file does not seem to be a Mnemosyne 1.x XML file."))
            raise MnemosyneError
        try:
            self.starttime = int(tree.getroot().get("time_of_start"))
        except:
            self.starttime = 0
        category_with_name = {}
        self.categories = []
        for element in tree.findall("category"):
            category = Mnemosyne1.MnemosyneCore.Category()
            category.name = element.find("name").text
            category.active = bool(element.get("active"))
            self.categories.append(category)
            category_with_name[category.name] = category
        self.items = []
        for element in tree.findall("item"):
            item = Mnemosyne1.MnemosyneCore.Item()
            item.id = element.get("id") 
            item.q = element.find("Q").text
            item.a = element.find("A").text
            item.cat = category_with_name[element.find("cat").text]
            try:
                item.grade = int(element.get("gr"))
            except:
                item.grade = 0
            try:
                item.easiness = float(element.get("e"))
            except:
                item.easiness = 2.5
            try:
                item.acq_reps = int(element.get("ac_rp"))
            except:
                item.acq_reps = 1
            try:
                item.ret_reps = int(element.get("rt_rp"))
            except:
                item.ret_reps = 0
            try:
                item.lapses = int(element.get("lps"))
            except:
                item.lapses = 0
            try:
                item.acq_reps_since_lapse = int(element.get("ac_rp_l"))
            except:
                item.acq_reps_since_lapse = 1
            try:
                item.ret_reps_since_lapse = int(element.get("rt_rp_l"))
            except:
                item.ret_reps_since_lapse = 0
            try:
                item.last_rep = int(element.get("l_rp"))
            except:
                item.last_rep = 0
            # This is how 1.x reads it, but why can next_rep be float
            # while last_rep can safely be parsed as an int?
            try:
                item.next_rep = int(float(element.get("n_rp")))
            except:
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
