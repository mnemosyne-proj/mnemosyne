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
        # Set up tag cache.
        tag_with_name = TagCache(self.component_manager)
        w = self.main_widget()
        # Open database.
        con = sqlite3.connect(filename)
        # Copy media directory.
        src = filename.replace(".anki2", ".media")
        dst = self.database().media_dir()
        for item in os.listdir(src):
            shutil.copy(os.path.join(src, item), os.path.join(dst, item))
        # Import collection table.
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
                card_type = MSided(self.component_manager)
                card_type.name = models[mid]["name"]
                card_type.id = clone_id="7::" + mid
                card_type.hidden_from_UI = False
                if card_type.id in self.component_manager.card_type_with_id:
                    # Don't import same card type twice.
                    continue
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
                    fact_view = FactView(template["name"],
                        card_type.id + "." + str(template["ord"]))
                    fact_view.extra_data["qfmt"] = template["qfmt"]
                    fact_view.extra_data["afmt"] = template["afmt"]
                    fact_view.extra_data["bqfmt"] = template["bqfmt"]
                    fact_view.extra_data["bafmt"] = template["bafmt"]
                    fact_view.extra_data["ord"] = template["ord"]
                    did = template["did"] # Deck id, ignore.
                    card_type.fact_views.append(fact_view)
                    self.database().add_fact_view(fact_view)
                mod = models[mid]["mod"] # Modification time, ignore.
                type = models[mid]["type"] # 0: standard, 1 cloze
                id = models[mid]["id"] # ignore
                css = models[mid]["css"]
                latex_preamble = models[mid]["latexPre"] # Ignore.
                latex_postamble = models[mid]["latexPost"] # Ignore.
                # Save to database.
                card_type.extra_data = {"css":css, "id":id, "type":type}
                self.database().add_card_type(card_type)
        # nid are Anki-internal indices for notes, so we need to temporarily
        # store some information.
        fact_for_nid = {}
        tag_names_for_nid = {}
        card_type_for_nid = {}
        # Import facts and tags.
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
            fact = Fact(fact_data, id=guid)
            self.database().add_fact(fact)
            fact_for_nid[id] = fact
            tag_names_for_nid[id] = tags
        # Import cards.
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
            card = Card(card_type, fact, fact_view, creation_time=creation_time)
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
            self.database().add_card(card)
        # Import logs.


        self.warned_about_missing_media = False

        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats(50)
        print(s.getvalue())