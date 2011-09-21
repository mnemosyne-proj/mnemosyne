#
# _mnemosyne1.py <Peter.Bienstman@UGent.be>
#                <Johannes.Baiter@gmail.com>
#

import os
import re
import shutil
import datetime
import calendar

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)
re_sound = re.compile(r"""<sound src=\".+?\">""", re.DOTALL | re.IGNORECASE)

class Mnemosyne1(object):

    # Dummy 1.x module strucutre
    class MnemosyneCore(object):                          
        class StartTime:                                    
            pass                                            
        class Category:                                     
            pass                                            
        class Item:                                         
            pass


    def _convert_to_2x(self):
        widget = self.main_widget()
        # See if the file was imported before.
        try:
            card = self.database().card(self.items[0].id,
                is_id_internal=False)
        except:
            card = None
        if card:
            widget.show_error(\
                _("This file seems to have been imported before. Aborting..."))
            return -2
        widget.set_progress_text(_("Importing cards..."))
        widget.set_progress_range(0, len(self.items))
        widget.set_progress_update_interval(len(self.items)/50)
        count = 0
        widget.set_progress_value(0)
        self.map_plugin_activated = False
        self.items_by_id = {}
        for item in self.items:
            if item.id in self.items_by_id:
                item.id = "dup" + item.id 
            self.items_by_id[item.id] = item
        for item in self.items:
            count += 1
            widget.set_progress_value(count)
            self._create_card_from_item(item)
        widget.set_progress_value(len(self.items))

    def _create_card_from_item(self, item):
        if item.cat.name == "<default>" or item.cat.name == "":
            item.cat.name = "__UNTAGGED__"
        # Don't create 'secondary' cards here, but create them together with
        # the 'main' card, except when the 'main' card has been deleted.
        if item.id.endswith(".inv") or item.id.endswith(".tr.1"):
            if not item.id.split(".", 1)[0] in self.items_by_id:
                card_type = self.card_type_with_id("1")
                fact_data = {"f": item.q, "b": item.a}
                tag_names = [item.cat.name]
                self._preprocess_media(fact_data, tag_names) 
                card = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=tag_names,
                    check_for_duplicates=False, save=False)[0]
                self._set_card_attributes(card, item)
            return True
        # Map.
        if item.id + ".inv" in self.items_by_id and \
            "answerbox: overlay" in item.q and "<img " in item.q:
            item_2 = self.items_by_id[item.id + ".inv"]
            loc = item_2.a
            marked = item_2.q
            blank = ""
            for match in re_src.finditer(item.q):
                blank = "<img %s>" % match.group()
            if self.map_plugin_activated == False:
                self._activate_map_plugin()
                self.map_plugin_activated = True
            card_type = self.card_type_with_id("4")
            fact_data = {"loc": loc, "marked": marked, "blank": blank}
            tag_names=[item.cat.name]
            self._preprocess_media(fact_data, tag_names) 
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)
            self._set_card_attributes(card_2, item)
            self._set_card_attributes(card_1, item_2)
        # Front-to-back.
        elif item.id + ".inv" not in self.items_by_id and \
            item.id + ".tr.1" not in self.items_by_id:
            card_type = self.card_type_with_id("1")
            fact_data = {"f": item.q, "b": item.a}
            tag_names=[item.cat.name]
            self._preprocess_media(fact_data, tag_names) 
            card = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)[0]
            self._set_card_attributes(card, item)
        # Front-to-back and back-to-front.         
        elif item.id + ".inv" in self.items_by_id:
            card_type = self.card_type_with_id("2")
            fact_data = {"f": item.q, "b": item.a}
            tag_names=[item.cat.name]
            self._preprocess_media(fact_data, tag_names) 
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)
            self._set_card_attributes(card_1, item)
            self._set_card_attributes\
                (card_2, self.items_by_id[item.id + ".inv"])               
        # Vocabulary.
        elif item.id + ".tr.1" in self.items_by_id:
            card_type = self.card_type_with_id("3")
            try:
                p_1, m_1 = item.a.split("\n", 1)
            except:
                p_1, m_1 = "", item.a    
            fact_data = {"f": item.q, "p_1": p_1, "m_1": m_1}
            tag_names=[item.cat.name]
            self._preprocess_media(fact_data, tag_names) 
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)            
            self._set_card_attributes(card_1, item)
            self._set_card_attributes\
                (card_2, self.items_by_id[item.id + ".tr.1"])
            return True
    def _midnight_UTC(self, timestamp):
        try:
            date_only = datetime.date.fromtimestamp(timestamp)
        except ValueError:
            date_only = datetime.date.max
        return int(calendar.timegm(date_only.timetuple()))

    def _set_card_attributes(self, card, item):
        # Note that we cannot give cards a new id, otherwise the log server
        # would not know it was the same card.
        self.database().change_card_id(card, item.id)
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

    def _preprocess_media(self, fact_data, tag_names):
        missing_media = False
        media_dir = self.database().media_dir()
        # os.path.normpath does not convert Windows separators to Unix
        # separators, so we need to make sure we internally store Unix paths.
        for fact_key in fact_data:
            for match in re_src.finditer(fact_data[fact_key]):
                fact_data[fact_key] = \
                    fact_data[fact_key].replace(match.group(),
                    match.group().replace("\\", "/"))
        # Convert sound tags to audio tags.
        for fact_key in fact_data:
            for match in re_sound.finditer(fact_data[fact_key]):
                fact_data[fact_key] = fact_data[fact_key].replace(match.group(),
                    match.group().replace("<sound src", "<audio src"))
        # Copy files to media directory, creating subdirectories as we go.
        for fact_key in fact_data:
            for match in re_src.finditer(fact_data[fact_key]):
                filename = match.group(1)
                if not os.path.exists(filename) and \
                    not os.path.exists(expand_path(filename, self.import_dir)):
                    fact_data[fact_key] = \
                        fact_data[fact_key].replace(match.group(),
                        "src_missing=\"%s\"" % match.group(1))
                    missing_media = True
                    continue
                if not os.path.isabs(filename):
                    source = expand_path(filename, self.import_dir)
                    dest = expand_path(filename, media_dir)
                    directory = os.path.dirname(dest)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    shutil.copy(source, dest)
        if missing_media:
            tag_names.append(_("MISSING_MEDIA"))
            if not self.warned_about_missing_media:
                self.main_widget().show_information(\
 _("Warning: media files were missing. These cards have been tagged as MISSING_MEDIA. You must also change 'scr_missing' to 'scr' in the text of these cards."))
                # We ask the users to edit the cards, so that the necessary
                # media copying can take place when editing the card.
                # Otherwise, if the user just add the missing file to the
                # right (non-Mnemosyne) directory, this would not happen.
                self.warned_about_missing_media = True

    def _activate_map_plugin(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()

