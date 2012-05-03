#
# mnemosyne1.py <Peter.Bienstman@UGent.be>
#               <Johannes.Baiter@gmail.com>
#

import re
import datetime
import calendar

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_formats.media_preprocessor \
    import MediaPreprocessor, re_src


class Mnemosyne1(MediaPreprocessor):

    """Common code for the 1.x XML and mem importers."""

    class MnemosyneCore(object):

        """Dummy 1.x module structure."""

        class StartTime:
            pass
        class Category:
            pass
        class Item:
            pass

    def create_cards_from_mnemosyne1(self, extra_tag_name):
        w = self.main_widget()
        # See if the file was imported before.
        try:
            card = self.database().card(self.items[0].id, is_id_internal=False)
        except:
            card = None
        if card:
            w.show_error(\
                _("These cards seem to have been imported before. Aborting..."))
            raise MnemosyneError
        w.set_progress_text(_("Importing cards..."))
        w.set_progress_range(len(self.items))
        w.set_progress_update_interval(len(self.items)/50)
        self.map_plugin_activated = False
        self.items_by_id = {}
        for item in self.items:
            if item.id in self.items_by_id:
                item.id = "dup" + item.id
            self.items_by_id[item.id] = item
        for item in self.items:
            w.increase_progress(1)
            self.create_card_from_item(item, extra_tag_name)
        w.set_progress_value(len(self.items))

    def create_card_from_item(self, item, extra_tag_name):
        # Create tag names.
        if item.cat.name == "<default>" or item.cat.name == "":
            item.cat.name = "__UNTAGGED__"
        tag_names = [item.cat.name]
        if extra_tag_name:
            tag_names.append(extra_tag_name)
        # Don't create 'secondary' cards here, but create them together with
        # the 'main' card, except when the 'main' card has been deleted.
        if item.id.endswith(".inv") or item.id.endswith(".tr.1"):
            if not item.id.split(".", 1)[0] in self.items_by_id:
                card_type = self.card_type_with_id("1")
                fact_data = {"f": item.q, "b": item.a}
                tag_names = [item.cat.name]
                self.preprocess_media(fact_data, tag_names)
                card = self.controller().create_new_cards(fact_data,
                    card_type, grade=-1, tag_names=tag_names,
                    check_for_duplicates=False, save=False)[0]
                self.set_card_attributes(card, item)
            return
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
                self.activate_map_plugin()
                self.map_plugin_activated = True
            card_type = self.card_type_with_id("4")
            fact_data = {"loc": loc, "marked": marked, "blank": blank}
            self.preprocess_media(fact_data, tag_names)
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)
            self.set_card_attributes(card_2, item)
            self.set_card_attributes(card_1, item_2)
        # Front-to-back.
        elif item.id + ".inv" not in self.items_by_id and \
            item.id + ".tr.1" not in self.items_by_id:
            card_type = self.card_type_with_id("1")
            fact_data = {"f": item.q, "b": item.a}
            self.preprocess_media(fact_data, tag_names)
            card = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)[0]
            self.set_card_attributes(card, item)
        # Front-to-back and back-to-front.
        elif item.id + ".inv" in self.items_by_id:
            card_type = self.card_type_with_id("2")
            fact_data = {"f": item.q, "b": item.a}
            self.preprocess_media(fact_data, tag_names)
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)
            self.set_card_attributes(card_1, item)
            self.set_card_attributes\
                (card_2, self.items_by_id[item.id + ".inv"])
        # Vocabulary.
        elif item.id + ".tr.1" in self.items_by_id:
            card_type = self.card_type_with_id("3")
            try:
                p_1, m_1 = item.a.split("\n", 1)
            except:
                p_1, m_1 = "", item.a
            fact_data = {"f": item.q, "p_1": p_1, "m_1": m_1}
            self.preprocess_media(fact_data, tag_names)
            card_1, card_2 = self.controller().create_new_cards(fact_data,
                card_type, grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)
            self.set_card_attributes(card_1, item)
            self.set_card_attributes\
                (card_2, self.items_by_id[item.id + ".tr.1"])

    def midnight_UTC(self, timestamp):
        try:
            date_only = datetime.date.fromtimestamp(timestamp)
        except ValueError:
            date_only = datetime.date.max
        return int(calendar.timegm(date_only.timetuple()))

    def set_card_attributes(self, card, item):
        # Note that we cannot give cards a new id, otherwise the log server
        # would not know it was the same card.
        self.database().change_card_id(card, item.id)
        for attr in ["id", "grade", "easiness", "acq_reps", "ret_reps",
            "lapses", "acq_reps_since_lapse", "ret_reps_since_lapse"]:
            setattr(card, attr, getattr(item, attr))
        DAY = 24 * 60 * 60 # Seconds in a day.
        card.last_rep = \
            self.midnight_UTC(self.starttime + item.last_rep * DAY)
        card.next_rep = \
            self.midnight_UTC(self.starttime + item.next_rep * DAY)
        if not hasattr(item, "unseen"):
            item.unseen = True
        if item.unseen and item.grade in [0, 1]:
            card.grade = -1
            card.acq_reps = 0
            card.acq_reps_since_lapse = 0
            card.last_rep = -1
            card.next_rep = -1
        self.database().update_card(card)

    def activate_map_plugin(self):
        for plugin in self.plugins():
            if plugin.components != []:  # Safeguard for badly written plugins.
                component = plugin.components[0]
                if component.component_type == "card_type" \
                    and component.id == "4":
                    plugin.activate()

