#
# mnemosyne1_mem.py <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import shutil
import cPickle
import datetime
import calendar

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.file_format import FileFormat

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)
re_sound = re.compile(r"""<sound src=\".+?\">""", re.DOTALL | re.IGNORECASE)

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
        if item.unseen and item.grade in [0, 1]:
            card.grade = -1
            card.acq_reps = 0
            card.acq_reps_since_lapse = 0
            card.last_rep = -1
            card.next_rep = -1
        self.database().update_card(card)

    def _preprocess_media(self, fact_data):        
        mediadir = self.config().mediadir()
        # os.path.normpath does not convert Windows separators to Unix
        # separators, so we need to make sure we internally store Unix paths.
        for key in fact_data:
            for match in re_src.finditer(fact_data[key]):
                fact_data[key] = fact_data[key].replace(match.group(),
                            match.group().replace("\\", "/"))
        # Convert sound tags to audio tags.
        for key in fact_data:
            for match in re_sound.finditer(fact_data[key]):
                fact_data[key] = fact_data[key].replace(match.group(),
                            match.group().replace("sound", "audio"))
        # Copy files to media directory, creating subdirectories as we go.
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
                    source = expand_path(filename, self.importdir)
                    dest = expand_path(filename, mediadir)
                    if not os.path.exists(source):
                        self.main_widget().information_box(\
                            _("Missing media file") + " %s" % source)
                        fact_data[key] = fact_data[key].replace(match.group(),
                            "src_missing=\"%s\"" % match.group(1))
                    else:
                        shutil.copy(source, dest)

    def _activate_map_plugin(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
    
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
            self.starttime, self.categories, self.items = cPickle.load(memfile)
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
        progress.set_value(0)
        map_plugin_activated = False
        items_by_id = {}
        for item in self.items:
            if item.id in items_by_id:
               item.id = "dup" + item.id 
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
                        card_type, grade=-1, tag_names=[item.cat.name],
                        check_for_duplicates=False)[0]
                    self._set_card_attributes(card, item)
                continue
            if self.database().has_card_with_external_id(item.id):
                progress.set_value(len(self.items))
                self.main_widget().error_box(\
               _("This file seems to have been imported before. Aborting..."))
                return
            # Map.
            if item.id + ".inv" in items_by_id and \
                "answerbox: overlay" in item.q:
                item_2 = items_by_id[item.id + ".inv"]
                loc = item_2.a
                marked = item_2.q
                blank = ""
                for match in re_src.finditer(item.q):
                    blank = "<img %s>" % match.group()
                if map_plugin_activated == False:
                    self._activate_map_plugin()
                    map_plugin_activated = True
                card_type = self.card_type_by_id("4")
                fact_data = {"loc": loc, "marked": marked, "blank": blank}
                self._preprocess_media(fact_data) 
                card_1, card_2 = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name],
                    check_for_duplicates=False)
                self._set_card_attributes(card_2, item)
                self._set_card_attributes(card_1, item_2)
            # Front-to-back.
            elif item.id + ".inv" not in items_by_id and \
               item.id + ".tr.1" not in items_by_id:
                card_type = self.card_type_by_id("1")
                fact_data = {"q": item.q, "a": item.a}
                self._preprocess_media(fact_data) 
                card = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name],
                    check_for_duplicates=False)[0]
                self._set_card_attributes(card, item)
            # Front-to-back and back-to-front.         
            elif item.id + ".inv" in items_by_id:
                card_type = self.card_type_by_id("2")
                fact_data = {"q": item.q, "a": item.a}
                self._preprocess_media(fact_data) 
                card_1, card_2 = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name],
                    check_for_duplicates=False)
                self._set_card_attributes(card_1, item)
                self._set_card_attributes(card_2,
                                          items_by_id[item.id + ".inv"])               
            # Three-sided.
            elif item.id + ".tr.1" in items_by_id:
                card_type = self.card_type_by_id("3")
                try:
                    p, t = item.a.split("\n", 1)
                except:
                    p, t = "", item.a    
                fact_data = {"f": item.q, "p": p, "t": t}
                self._preprocess_media(fact_data) 
                card_1, card_2 = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=[item.cat.name],
                    check_for_duplicates=False)            
                self._set_card_attributes(card_1, item)
                self._set_card_attributes(card_2,
                                          items_by_id[item.id + ".tr.1"])  
        progress.set_value(len(self.items))
        
