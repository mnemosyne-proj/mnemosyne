#
#  anki2.py Peter.Bienstman@UGent.be>
#

import os
import re
import json
import time
import shutil
import sqlite3

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.card_types.M_sided import MSided
from mnemosyne.libmnemosyne.file_formats.media_preprocessor \
    import MediaPreprocessor

sound_re = re.compile("(?i)(\[sound:(?P<fname>[^]]+)\])")


class TagCache(dict, Component):

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self._tags_with_name = {}

    def __getitem__(self, tag_name):
        if not tag_name in self._tags_with_name:
            self._tags_with_name[tag_name] = \
                self.database().get_or_create_tag_with_name(tag_name)
        return self._tags_with_name[tag_name]


class Anki2(FileFormat, MediaPreprocessor):

    description = _("Anki2 collections")
    extension = ".anki2"
    filename_filter = _("Anki2 files (*.anki2)")
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def do_import(self, filename, extra_tag_names=""):
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()

        FileFormat.do_import(self, filename, extra_tag_names)
        w = self.main_widget()
        db = self.database()
        # Set up tag cache.
        tag_with_name = TagCache(self.component_manager)
        # Open database.
        con = sqlite3.connect(filename)
        # Copy media directory.
        w.set_progress_text(_("Copying media files..."))
        src = filename.replace(".anki2", ".media")
        dst = db.media_dir()
        number_of_files = len(os.listdir(src))
        w.set_progress_range(number_of_files)
        w.set_progress_update_interval(number_of_files/50)
        for item in os.listdir(src):
            shutil.copy(os.path.join(src, item), os.path.join(dst, item))
            w.increase_progress(1)
        # Import collection table.
        w.set_progress_text(_("Importing card types..."))
        # Too few in number to warrant counted progress bar.
        card_type_for_mid = {}  # mid: model id
        deck_name_for_did = {}  # did: deck id
        for id, crt, mod, scm, ver, dty, usn, ls, conf, models, decks, \
            dconf, tags in con.execute("""select id, crt, mod, scm, ver, dty,
            usn, ls, conf, models, decks, dconf, tags from col"""):
            # crt: creation time, ignore.
            # mod: modification time, ignore.
            # scm: TODO
            # ver: schema version, ignore.
            # dty: TODO
            # usn: syncing related, ignore.
            # ls: TODO
            # conf: configuration, ignore.
            # dconf: deck configuration, ignore.
            # tags: list of tags, but they turn up later in the notes, ignore.

            # Decks will be converted to Tags when creating cards.
            decks = json.loads(decks)
            for did in decks:
                deck_name_for_did[int(did)] = decks[did]["name"]
            # Models will be converted to CardTypes
            models = json.loads(models)
            for mid in models:  # mid: model id
                card_type_id = "7::" + mid
                card_type_already_imported = \
                    db.has_card_type_with_id(card_type_id)
                if card_type_already_imported:
                    card_type = self.component_manager.card_type_with_id[\
                        card_type_id]
                else:
                    card_type = MSided(self.component_manager)
                card_type.name = models[mid]["name"]
                card_type.id = card_type_id
                card_type.hidden_from_UI = False
                card_type_for_mid[int(mid)] = card_type
                vers = models[mid]["vers"] # Version, ignore.
                tags = models[mid]["tags"] # TODO, seems empty
                did = models[mid]["did"] # Deck id, ignore.
                usn = models[mid]["usn"] # Syncing related, ignore.
                if "req" in models[mid]:
                    required = models[mid]["req"] # TODO,"req": [[0, "all", [0]]], "
                else:
                    required = []
                flds = models[mid]["flds"]
                flds.sort(key=lambda x : x["ord"])
                card_type.fact_keys_and_names = []
                for field in flds:
                    card_type.fact_keys_and_names.append(\
                        (str(field["ord"]), field["name"]))
                    media = field["media"] # TODO
                    sticky = field["sticky"] # Sticky field, ignore.
                    rtl = field["rtl"] # Text direction, ignore.
                    font = field["font"] # TODO
                    size = field["size"] # TODO
                sortf = models[mid]["sortf"] # Sorting field, ignore. TODO: related to unique?
                tmpls = models[mid]["tmpls"]
                tmpls.sort(key=lambda x : x["ord"])
                # Fact views.
                card_type.fact_views = []
                for template in tmpls:
                    fact_view_id = card_type.id + "." + str(template["ord"])
                    fact_view_already_imported = \
                        db.has_fact_view_with_id(fact_view_id)
                    if fact_view_already_imported:
                        fact_view = db.fact_view(\
                            fact_view_id, is_id_internal=False)
                        fact_view.name = template["name"]
                    else:
                        fact_view = FactView(template["name"], fact_view_id)
                    fact_view.extra_data["qfmt"] = template["qfmt"]
                    fact_view.extra_data["afmt"] = template["afmt"]
                    fact_view.extra_data["bqfmt"] = template["bqfmt"]
                    fact_view.extra_data["bafmt"] = template["bafmt"]
                    fact_view.extra_data["ord"] = template["ord"]
                    did = template["did"] # Deck id, ignore.
                    card_type.fact_views.append(fact_view)
                    if fact_view_already_imported:
                        db.update_fact_view(fact_view)
                    else:
                        db.add_fact_view(fact_view)
                mod = models[mid]["mod"] # Modification time, ignore.
                type = models[mid]["type"] # 0: standard, 1 cloze
                id = models[mid]["id"]
                css = models[mid]["css"]
                latex_preamble = models[mid]["latexPre"] # Ignore.
                latex_postamble = models[mid]["latexPost"] # Ignore.
                # Save to database.
                card_type.extra_data = {"css":css, "id":id, "type":type}
                if card_type_already_imported:
                    db.update_card_type(card_type)
                else:
                    db.add_card_type(card_type)
        # nid are Anki-internal indices for notes, so we need to temporarily
        # store some information.
        tag_names_for_nid = {}
        card_type_for_nid = {}
        # Import facts and tags.
        w.set_progress_text(_("Importing notes..."))
        number_of_notes = con.execute("select count() from notes").fetchone()[0]
        w.set_progress_range(number_of_notes)
        w.set_progress_update_interval(number_of_notes/20)
        fact_for_nid = {}
        for id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data in \
            con.execute("""select id, guid, mid, mod, usn, tags, flds, sfld,
            csum, flags, data from notes"""):
            # mod: modification time, ignore.
            # usn: syncing related, ignore.
            # sfld: sorting field, ignore.
            # csum: checksum? TODO
            # flags: TODO
            # data: TODO
            card_type = card_type_for_mid[int(mid)]
            card_type_for_nid[id] = card_type
            fields = flds.split("\x1f")
            assert (len(fields) == len(card_type.fact_keys_and_names))
            fact_data = {}
            for i in range(len(fields)):
                fact_key = card_type.fact_keys_and_names[i][0]
                data = fields[i]
                # Deal with sound tags.
                for match in sound_re.finditer(data):
                    fname = match.group("fname")
                    data = data.replace(\
                        match.group(0), "<audio src=\"" + fname + "\">")
                # Deal with latex tags.
                data = data.replace("[latex]", "<latex>")
                data = data.replace("[/latex]", "</latex>")
                data = data.replace("[$]", "<$>")
                data = data.replace("[/$]", "</$>")
                data = data.replace("[$$]", "<$$>")
                data = data.replace("[/$$]", "</$$>")
                fact_data[fact_key] = data
            if db.has_fact_with_id(guid):
                fact = db.fact(guid, is_id_internal=False)
                fact.data = fact_data
                db.update_fact(fact)
            else:
                fact = Fact(fact_data, id=guid)
                db.add_fact(fact)
            fact_for_nid[id] = fact
            tag_names_for_nid[id] = tags
            w.increase_progress(1)
        # Import cards.
        w.set_progress_text(_("Importing cards..."))
        number_of_cards = con.execute("select count() from cards").fetchone()[0]
        w.set_progress_range(number_of_cards)
        w.set_progress_update_interval(number_of_cards/20)
        for id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, \
            lapses, left, odue, odid, flags, data in con.execute("""select id,
            nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps,
            lapses, left, odue, odid, flags, data from cards"""):
            # type: 0=new, 1=learning, 2=due: ignore
            # queue: same as above, and -1=suspended,
            #        -2=user buried, -3=sched buried
            # due is used differently for different queues.
            # - new queue: note id or random int
            # - rev queue: integer day
            # - lrn queue: integer timestamp
            # TODO
            # queue: use suspended status to set card inactive?
            # mod: modification time?
            # usn: syncing related, ignore.
            # due,
            # ivl,
            # factor,
            # reps,
            # lapses,
            # left,
            # odue,
            # odid,
            # flags,
            # data
            fact = fact_for_nid[nid]
            card_type = card_type_for_nid[nid]
            creation_time = time.time() # TODO
            if card_type.extra_data["type"] == 0:
                fact_view = card_type.fact_views[ord]
            else:  # Cloze.
                fact_view = card_type.fact_views[0]
            already_imported = db.has_card_with_id(id)
            if already_imported:
                card = db.card(id, is_id_internal=False)
                card.card_type = card_type
                card.fact = fact
                card.fact_view = fact_view
                card.creation_time = creation_time
            else:
                card = Card(card_type, fact, fact_view,
                            creation_time=creation_time)
            card.id = id
            card.extra_data["ord"] = ord  # Needed separately for clozes.
            tag_names = [tag_name.strip() for \
                             tag_name in extra_tag_names.split(",")]
            tag_names += [tag_name.strip() for \
                             tag_name in tag_names_for_nid[nid].split(" ")]
            tag_names += [deck_name_for_did[did].strip().replace(",", ";")]
            for tag_name in tag_names:
                if tag_name:
                    card.tags.add(tag_with_name[tag_name])
            #card.grade = sql_res[5]
            #card.next_rep = sql_res[6]
            #card.last_rep = sql_res[7]
            #card.easiness = sql_res[8]
            #card.acq_reps = sql_res[9]
            #card.ret_reps = sql_res[10]
            #card.lapses = sql_res[11]
            #card.acq_reps_since_lapse = sql_res[12]
            #card.ret_reps_since_lapse = sql_res[13]
            #card.modification_time = sql_res[15]
            #self._construct_extra_data(sql_res[16], card)
            #card.scheduler_data = sql_res[17]
            #card.active = sql_res[18]
            if already_imported:
                db.update_card(card)
            else:
                db.add_card(card)
            w.increase_progress(1)
        # Import logs.
        w.set_progress_text(_("Importing logs..."))
        number_of_logs = con.execute("select count() from revlog").fetchone()[0]
        w.set_progress_range(number_of_logs)
        w.set_progress_update_interval(number_of_logs/20)

        w.close_progress()
        self.warned_about_missing_media = False

        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(50)
        print(s.getvalue())