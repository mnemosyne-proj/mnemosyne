#
# mnemosyne2_cards.py <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import time
import cPickle

from openSM2sync.log_entry import LogEntry
from openSM2sync.log_entry import EventTypes
from openSM2sync.text_formats.xml_format import XMLFormat

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat

re_src = re.compile(r"""src=['\"](.+?)['\"]""", re.DOTALL | re.IGNORECASE)


class Mnemosyne2Cards(FileFormat):

    description = _("Mnemosyne 2.x *.cards files")
    filename_filter = _("Mnemosyne 2.x cards for sharing (*.cards)")
    import_possible = True
    export_possible = True

    def do_export(self, filename):
        FileFormat.do_export(self, filename)
        db = self.database()
        w = self.main_widget()
        w.set_progress_text(_("Exporting cards..."))
        # Active facts (working with python sets turns out to be more
        # efficient than a 'distinct' statement in SQL).
        _fact_ids = list(set([cursor[0] for cursor in db.con.execute(\
            "select _fact_id from cards where active=1")]))
        # Active cards and their inactive sister cards.
        # (We need to log cards too instead of just facts, otherwise we cannot
        # communicate the card type.)
        _card_ids = [cursor[0] for cursor in db.con.execute(\
            """select _id from cards where _fact_id in
            (select _fact_id from cards where active=1)""")]
        # Tags belonging to the active cards.
        tags = db.tags_from_cards_with_internal_ids(_card_ids)
        # User defined card types.
        defined_in_database_ids = set([cursor[0] for cursor in \
            db.con.execute("select id from card_types")])
        # Card types of the active cards (no need to include inactive sister
        # cards here, as they share the same card type).
        active_card_type_ids = set([cursor[0] for cursor in db.con.execute(\
            "select card_type_id from cards where active=1")]).\
            intersection(defined_in_database_ids)
        # Also add parent card types, even if they are not active at the
        # moment.
        parent_card_type_ids = set()
        for id in active_card_type_ids:
            while "::" in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit("::", 1)
                if id in defined_in_database_ids and \
                    id not in active_card_type_ids:
                    parent_card_type_ids.add(id)
        card_type_ids = active_card_type_ids.union(parent_card_type_ids)
        # Fact views.
        fact_view_ids = []
        for card_type_id in card_type_ids:
            fact_view_ids += eval(db.con.execute(\
                "select fact_view_ids from card_types where id=?",
                (card_type_id, )).fetchone()[0])
        # Media files for active cards.
        db.dynamically_create_media_files()
        media_filenames = set()
        for result in db.con.execute(\
            """select value from data_for_fact where _fact_id in (select
            _fact_id from cards where active=1) and value like '%src=%'"""):
            for match in re_src.finditer(result[0]):
                media_filenames.add(match.group(1))
        # Generate log entries.
        number_of_entries = len(tags) + len(fact_view_ids) + \
            len(card_type_ids) + len(media_filenames) + \
            len(_card_ids) + len(_fact_ids)
        outfile = file("cards.xml", "w")

        # TMP
        outfile = file("test.cards", "w")


        xml_format = XMLFormat()
        outfile.write(xml_format.log_entries_header(number_of_entries))
        for tag in tags:
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_TAG
            log_entry["o_id"] = tag.id
            log_entry["name"] = tag.name
            outfile.write(xml_format.repr_log_entry(log_entry))
        for fact_view_id in fact_view_ids:
            fact_view = db.fact_view(fact_view_id, is_id_internal=False)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_FACT_VIEW
            log_entry["o_id"] = fact_view.id
            log_entry["name"] = fact_view.name
            log_entry["q_fact_keys"] = repr(fact_view.q_fact_keys)
            log_entry["a_fact_keys"] = repr(fact_view.a_fact_keys)
            log_entry["q_fact_key_decorators"] = \
                repr(fact_view.q_fact_key_decorators)
            log_entry["a_fact_key_decorators"] = \
                repr(fact_view.a_fact_key_decorators)
            log_entry["a_on_top_of_q"] = repr(fact_view.a_on_top_of_q)
            log_entry["type_answer"] = repr(fact_view.type_answer)
            if fact_view.extra_data:
                log_entry["extra"] = repr(fact_view.extra_data)
            outfile.write(xml_format.repr_log_entry(log_entry))
        for card_type_id in card_type_ids:
            card_type = db.card_type(card_type_id, is_id_internal=False)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_CARD_TYPE
            log_entry["o_id"] = card_type.id
            log_entry["name"] = card_type.name
            log_entry["fact_keys_and_names"] = \
                repr(card_type.fact_keys_and_names)
            log_entry["fact_views"] = repr([fact_view.id for fact_view \
                in card_type.fact_views])
            log_entry["unique_fact_keys"] = \
                repr(card_type.unique_fact_keys)
            log_entry["required_fact_keys"] = \
                repr(card_type.required_fact_keys)
            log_entry["keyboard_shortcuts"] = \
                repr(card_type.keyboard_shortcuts)
            if card_type.extra_data:
                log_entry["extra"] = repr(card_type.extra_data)
            outfile.write(xml_format.repr_log_entry(log_entry))
        for media_filename in media_filenames:
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_MEDIA_FILE
            log_entry["fname"] = media_filename
            outfile.write(xml_format.repr_log_entry(log_entry))
        for _fact_id in _fact_ids:
            fact = db.fact(_fact_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_FACT
            log_entry["o_id"] = fact.id
            for fact_key, value in fact.data.iteritems():
                log_entry[fact_key] = value
            outfile.write(xml_format.repr_log_entry(log_entry))
        for _card_id in _card_ids:
            card = db.card(_card_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_CARD
            log_entry["o_id"] = card.id
            log_entry["card_t"] = card.card_type.id
            log_entry["fact"] = card.fact.id
            log_entry["fact_v"] = card.fact_view.id
            log_entry["tags"] = ",".join([tag.id for tag in card.tags])
            log_entry["c_time"] = -666 # To be replace by import time.
            log_entry["gr"] = card.grade
            log_entry["e"] = card.easiness
            log_entry["ac_rp"] = card.acq_reps
            log_entry["rt_rp"] = card.ret_reps
            log_entry["lps"] = card.lapses
            log_entry["ac_rp_l"] = card.acq_reps_since_lapse
            log_entry["rt_rp_l"] = card.ret_reps_since_lapse
            log_entry["l_rp"] = card.last_rep
            log_entry["n_rp"] = card.next_rep
            outfile.write(xml_format.repr_log_entry(log_entry))
        outfile.write(xml_format.log_entries_footer())
        outfile.close()
        w.close_progress()

    def do_import(self, filename, extra_tag_name=None):
        FileFormat.do_import(self, filename, extra_tag_name)
        w = self.main_widget()
        w.set_progress_text(_("Importing cards..."))
        self.database().card_types_to_instantiate_later = set()
        element_loop = XMLFormat().parse_log_entries(file(filename))
        number_of_entries = int(element_loop.next())
        if number_of_entries == 0:
            return
        w.set_progress_range(number_of_entries)
        w.set_progress_update_interval(number_of_entries/50)
        for log_entry in element_loop:
            self.database().apply_log_entry(log_entry)
            w.increase_progress(1)
        w.set_progress_value(number_of_entries)
        if len(self.database().card_types_to_instantiate_later) != 0:
            raise RuntimeError, _("Missing plugins for card types.")




