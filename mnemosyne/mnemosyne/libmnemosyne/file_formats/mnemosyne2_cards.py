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
        #FileFormat.do_export(self, filename)
        w = self.main_widget()
        w.set_progress_text(_("Exporting cards..."))

        self.con = self.database().con

        import time
        t = time.time()

        # TODO: move these queries to SQLite python filese

        # Get active facts (working with python sets turns out to be more
        # efficient than a 'distinct' statement in SQL).
        _fact_ids = list(set([cursor[0] for cursor in self.con.execute(\
            "select _fact_id from cards where active=1")]))

        # Get the active cards and their inactive sister cards.
        # (We need to log them to communicate the card type too)

        _card_ids = [cursor[0] for cursor in self.con.execute(\
            """select _id from cards where _fact_id in
            (select _fact_id from cards where active=1)""")]

        # Get tags belonging to the active cards.
        tags = self.database().tags_from_cards_with_internal_ids(_card_ids)

        # Get card types needed for the active cards (no need to include
        # inactive sister cards here, as they share the same card type).
        card_type_ids = list(set([cursor[0] for cursor in self.con.execute(\
            "select card_type_id from cards where active=1")]))
        # TODO: add parent card types

        # TODO; fact views

        print time.time() - t

        t = time.time()

        # Get media files for active cards.
        self.database().dynamically_create_media_files()
        media_files = set()
        for result in self.con.execute(\
            """select value from data_for_fact where _fact_id in (select
            _fact_id from cards where active=1) and value like '%src=%'"""):
            for match in re_src.finditer(result[0]):
                media_files.add(match.group(1))

        print 'media', time.time() - t


        # Generate log entries.

        xml_format = XMLFormat()

        for tag in tags:
            # can reuse sqlite sync, but id vs _id, extra data
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_TAG
            log_entry["o_id"] = tag.id
            log_entry["name"] = tag.name
            print xml_format.repr_log_entry(log_entry)

        # for card type, fact views, media, we can reuse sqlite sync

        for _fact_id in _fact_ids:
            # can reuse, but need to spoof capabilities
            fact = self.database().fact(_fact_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_FACT
            log_entry["o_id"] = fact.id
            for fact_key, value in fact.data.iteritems():
                log_entry[fact_key] = value
            print xml_format.repr_log_entry(log_entry)
        for _card_id in _card_ids:
            # can reuse, but only needs limited data.
            card = self.database().card(_card_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_CARD
            log_entry["card_t"] = card.card_type.id
            log_entry["fact"] = card.fact.id
            log_entry["fact_v"] = card.fact_view.id
            log_entry["tags"] = ",".join([tag.id for tag in card.tags])
            print xml_format.repr_log_entry(log_entry)


        # TODO: metadata


        w.close_progress()

    def do_import(self, filename, extra_tag_name=None):
        FileFormat.do_import(self, filename, extra_tag_name)
        w = self.main_widget()
        w.set_progress_text(_("Importing cards..."))

        # set database.syncing to true. Rename it to importing?


        # TODO: creation date should be import date, not export date.

        # TODO: if fact exists, overwrite