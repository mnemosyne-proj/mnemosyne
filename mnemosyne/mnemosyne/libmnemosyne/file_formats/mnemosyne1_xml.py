#
# mnemosyne1_xml.py <Johannes.Baiter@gmail.com>
#

import os.path
import time
from xml.etree import cElementTree

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.file_formats.mnemosyne1 import Mnemosyne1
from mnemosyne.libmnemosyne.file_format import FileFormat

class Mnemosyne1XML(FileFormat, Mnemosyne1):

    description = _("Mnemosyne 1.x *.xml files")
    filename_filter = _("Mnemosyne 1.x XML files") + " (*.xml)"
    import_possible = True
    export_possible = False

    def do_import(self, filename, tag_name=None, reset_learning_data=False):
        db = self.database()
        # Manage database indexes.
        db.before_mem_import()
        log_index = db.current_log_index()
        result = self._import_xml_file(filename, tag_name, reset_learning_data)
        db.remove_card_log_entries_since(log_index)
        db.after_mem_import()
        # Return if something went wrong
        # TODO: This is a very unidiomatic, refactor to use Exceptions
        if result and result < 0:
            return result
        db.dump_to_science_log()
        db.skip_science_log()
        # Force an ADDED_CARD log entry for our cards.
        db.add_missing_added_card_log_entries(\
            set(item.id for item in self.items))
        # In 2.x, repetition events are used to update a card's last_rep and
        # next_rep during sync. In 1.x, there was no such information,
        # therefore, we force a card edit event for all cards.
        timestamp = int(time.time())
        for item in self.items:
            db.log_edited_card(timestamp, item.id)
        db.link_inverse_cards()
        db.save()
        return result

    def _import_xml_file(self, filename, tag_name=None,
                         reseat_learning_data=False):
        self.import_dir = os.path.dirname(os.path.abspath(filename))
        self.warned_about_missing_media = False
        try:
            tree = cElementTree.parse(filename)
        except:
            self.main_widget().show_error(
                    _("Unable to open file."))
            return -1
        if tree.getroot().tag != 'mnemosyne':
            self.main_widget().show_error(_
                    ("Bad XML File: Needs to be an Mnemosyne 1.x XML file."))
            return -1
        if tree.getroot().get('core_version') != '1':
            self.main_widget().show_error(_
                    ("Bad file version: Needs to be an Mnemosyne 1.x XML file."))
            return -1
        self.starttime = int(tree.getroot().get('time_of_start'))
        catdict = {}
        self.categories = []
        for element in tree.findall('category'):
            category = Mnemosyne1.MnemosyneCore.Category()
            category.name = element.find('name').text
            category.active = bool(element.get('active'))
            self.categories.append(category)
            catdict[category.name] = category
        self.items = []
        for element in tree.findall('item'):
            item = Mnemosyne1.MnemosyneCore.Item()
            item.id = element.get('id') 
            item.q = element.find('Q').text
            item.a = element.find('A').text
            item.cat = catdict[element.find('cat').text]
            item.grade = int(element.get('gr'))
            item.easiness = float(element.get('e'))
            item.acq_reps = int(element.get('ac_rp'))
            item.ret_reps = int(element.get('rt_rp'))
            item.lapses = int(element.get('lps'))
            item.acq_reps_since_lapse = int(element.get('ac_rp_l'))
            item.ret_reps_since_lapse = int(element.get('rt_rp_l'))
            item.last_rep = int(element.get('l_rp'))
            # This is how 1.x reads it, but why can next_rep be float
            # while last_rep can safely be parsed as an int?
            item.next_rep = int(float(element.get('n_rp')))
            if element.get('u'):
                item.unseen = bool(element.get('u'))
            else:
                if item.acq_reps <= 1 and item.ret_reps == 0\
                        and item.grade == 0:
                    item.unseen = True
                else:
                    item.unseen = False
            self.items.append(item)
        return self._convert_to_2x()

