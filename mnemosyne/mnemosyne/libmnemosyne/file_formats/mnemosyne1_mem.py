#
# mnemosyne1_mem.py <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import pickle
import shutil
import datetime
import calendar

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.file_format import FileFormat

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)


class Mnemosyne1Mem(FileFormat):
    
    description = _("Mnemosyne 1.x *.mem files")
    filename_filter = _("Mnemosyne 1.x databases") + " (*.mem)"
    import_possible = True
    export_possible = False

    def _midnight_UTC(self, timestamp):
        date_only = datetime.date.fromtimestamp(timestamp)
        return int(calendar.timegm(date_only.timetuple()))
    
    def _set_card_attributes(self, card, item):
        for attr in ["id", "grade", "easiness", "acq_reps", "ret_reps",
                "lapses", "acq_reps_since_lapse", "ret_reps_since_lapse"]:
            setattr(card, attr, getattr(item, attr))    
        DAY = 24 * 60 * 60 # Seconds in a day.
        card.last_rep = \
                      self._midnight_UTC(self.starttime + item.last_rep * DAY)
        card.next_rep = \
                      self._midnight_UTC(self.starttime + item.next_rep * DAY)
        if item.unseen and item.grade < 2:
            card.grade = -1
            card.acq_reps = 0
            card.acq_reps_since_lapse = 0
            card.last_rep = -1
            card.next_rep = -1
        self.database().update_card(card)

    def _preprocess_media(self, fact_data):

        "Copy file to media directory, creating subdirectories as we go."
        
        mediadir = self.config().mediadir()
        for key in fact_data:
            for match in re_src.finditer(fact_data[key]):
                filename = match.group(1)
                if not os.path.isabs(filename):
                    subdir = os.path.dirname(filename)
                    subdirs = []
                    while subdir:
                        subdirs.insert(0, os.path.join(mediadir, subdir))
                        subdir = os.path.dirname(subdir)
                    for subdir in subdirs:
                        if not os.path.exists(subdir):
                            os.mkdir(subdir)
                    shutil.copy(expand_path(filename, self.importdir),
                                expand_path(filename, mediadir))
    
    def do_import(self, filename, tag_name=None, reset_learning_data=False):
        self.importdir = os.path.dirname(os.path.abspath(filename))
        
        # Mimick 1.x module structure.
        class MnemosyneCore(object):                          
            class StartTime:                                    
                pass                                            
            class Category:                                     
                pass                                            
            class Item:                                         
                pass
        sys.modules["mnemosyne.core"] = object()       
        sys.modules["mnemosyne.core.mnemosyne_core"] = MnemosyneCore()
        
        # Load data.
        try:                                                    
            memfile = file(filename, "rb")
            header = memfile.readline()
            self.starttime, self.categories, self.items = pickle.load(memfile)
            self.starttime = self.starttime.time
        except:
            self.main_widget().error_box(_("Unable to open file."))
            return
            
        # Convert to 2.x data structures.
        progress = self.component_manager.get_current("progress_dialog")\
                   (self.component_manager)
        progress.set_text(_("Importing cards..."))
        progress.set_range(0, len(self.items))
        update_interval = int(len(self.items)/50)
        if update_interval == 0:
            update_interval = 1
        count = 0
        import time
        t0 = time.time()
        progress.set_value(0)
        items_by_id = {}
        for item in self.items:
            items_by_id[item.id] = item
        for item in self.items:
            count += 1
            if count % update_interval == 0:
                progress.set_value(count)
            if item.id.endswith(".inv") or item.id.endswith(".tr.1"):
                if not item.id.split(".", 1)[0] in items_by_id:
                    # Orphaned 2 or 3 sided card.
                    card_type = self.card_type_by_id("1")
                    fact_data = {"q": item.q, "a": item.a}
                    self._preprocess_media(fact_data) 
                    card = self.controller().create_new_cards(fact_data,
                        card_type, grade=-1, tag_names=[item.cat.name])[0]
                    self._set_card_attributes(card, item)
                continue
            # Front-to-back.
            if item.id + ".inv" not in items_by_id and \
               item.id + ".tr.1" not in items_by_id:
                card_type = self.card_type_by_id("1")
                fact_data = {"q": item.q, "a": item.a}
                self._preprocess_media(fact_data) 
                card = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name])[0]
                self._set_card_attributes(card, item)
            # Front-to-back and back-to-front.         
            if item.id + ".inv" in items_by_id:
                card_type = self.card_type_by_id("2")
                fact_data = {"q": item.q, "a": item.a}
                self._preprocess_media(fact_data) 
                card_1, card_2 = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name])
                self._set_card_attributes(card_1, item)
                self._set_card_attributes(card_2,
                                          items_by_id[item.id + ".inv"])               
            # Three-sided.
            if item.id + ".tr.1" in items_by_id:
                card_type = self.card_type_by_id("3")
                try:
                    p, t = item.a.split("\n", 1)
                except:
                    p, t = "", item.a    
                fact_data = {"f": item.q, "p": p, "t": t}
                self._preprocess_media(fact_data) 
                card_1, card_2 = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name])            
                self._set_card_attributes(card_1, item)
                self._set_card_attributes(card_2,
                                          items_by_id[item.id + ".tr.1"])  
        progress.set_value(len(self.items))
        print time.time()-t0

        # 4.2 sec
        # with cat: 4.6
        # card type check: same
        # with related cards: 5.2
        # with time field: 5.7
        # copying media: 6.5

