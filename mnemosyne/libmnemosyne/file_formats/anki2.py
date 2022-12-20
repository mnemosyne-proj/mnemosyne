#
#  anki2.py Peter.Bienstman@gmail.com>
#

import os
import re
import json
import time
import shutil
import sqlite3
import zipfile

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.card_types.M_sided import MSided
from mnemosyne.libmnemosyne.criteria.default_criterion import \
     DefaultCriterion
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
    filename_filter = _("Anki2 collections (*.anki2 *.apkg)")
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def extract_apkg(self, filename):
        # Extract zipfile.
        w = self.main_widget()
        w.set_progress_text(_("Decompressing..."))
        zip_file = zipfile.ZipFile(filename, "r")
        tmp_dir = os.path.join(os.path.dirname(filename), "__TMP__")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        zip_file.extractall(tmp_dir)
        # Rename media.
        media_file_with_id = json.loads(\
            open(os.path.join(tmp_dir, "media")).read())
        number_of_files = len(media_file_with_id)
        w.set_progress_text(_("Processing media files..."))
        w.set_progress_range(number_of_files)
        w.set_progress_update_interval(number_of_files/50)
        media_dir = os.path.join(tmp_dir, "collection.media")
        os.mkdir(media_dir)
        for id, media_file in media_file_with_id.items():
            w.increase_progress(1)
            if media_file.startswith("latex-"):
                continue
            os.rename(os.path.join(tmp_dir, id),
                      os.path.join(media_dir, media_file))
        # Note: Anki itself goes through some trouble of making sure ids
        # are unique and updating them if needed, because their id scheme
        # is very sensitive to collisions. We decided not to do that here
        # because it would break being able to reimport an updated version
        # of the cards.
        return tmp_dir

    def do_import(self, filename, extra_tag_names=""):
        self.main_widget().show_information(_(\
"Note that while you can edit imported cards, adding new cards to Anki's card types is currently not supported.\n\nAlso, in case you run into problems, don't hesitate to contact the developers."))
        FileFormat.do_import(self, filename, extra_tag_names)
        w = self.main_widget()
        db = self.database()
        # Preprocess apkg files.
        tmp_dir = None
        if filename.endswith(".apkg"):
            tmp_dir = self.extract_apkg(filename)
            filename = os.path.join(tmp_dir, "collection.anki2" )
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
            # mod: modification time, ignore.
            # scm: schema modification time, ignore.
            # ver: schema version, ignore.
            # dty: no longer used according to Anki source.
            # usn: syncing related, ignore.
            # ls: last sync, ignore.
            # conf: configuration, ignore.
            # dconf: deck configuration, ignore.
            # tags: list of tags, but they turn up later in the notes, ignore.
            collection_creation_time = crt
            decks = json.loads(decks)
            # Decks will be converted to Tags when creating cards.
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
                #vers = models[mid]["vers"] # Optional version, ignore.
                #tags = models[mid]["tags"] # Seems empty, ignore.
                #did = models[mid]["did"] # Deck id, ignore.
                #usn = models[mid]["usn"] # Syncing related, ignore.
                if "req" in models[mid]:
                    required = models[mid]["req"]
                    # Cache for a calculation to determine which fields are
                    # required. "req": [[0, "all", [0]]]
                    # Not yet implemented.
                else:
                    required = []
                flds = models[mid]["flds"]
                flds.sort(key=lambda x : x["ord"])
                card_type.fact_keys_and_names = []
                for field in flds:
                    card_type.fact_keys_and_names.append(\
                        (str(field["ord"]), field["name"]))
                    #media = field["media"] # Reserved for future use, ignore.
                    #sticky = field["sticky"] # Sticky field, ignore.
                    #rtl = field["rtl"] # Text direction, ignore.
                    font_string = field["font"] + "," + str(field["size"]) + \
                        ",-1,5,50,0,0,0,0,0,Regular"
                    self.config().set_card_type_property("font", font_string,
                        card_type, str(field["ord"]))
                #sortf = models[mid]["sortf"] # Sorting field, ignore.
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
                    #did = template["did"] # Deck id, ignore.
                    card_type.fact_views.append(fact_view)
                    if fact_view_already_imported:
                        db.update_fact_view(fact_view)
                    else:
                        db.add_fact_view(fact_view)
                #mod = models[mid]["mod"] # Modification time, ignore.
                type_ = models[mid]["type"] # 0: standard, 1 cloze
                id = models[mid]["id"]
                css = models[mid]["css"]
                #latex_preamble = models[mid]["latexPre"] # Ignore.
                #latex_postamble = models[mid]["latexPost"] # Ignore.
                # Save to database.
                card_type.extra_data = {"css":css, "id":id, "type":type_}
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
        modification_time_for_nid = {}
        for id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data in \
            con.execute("""select id, guid, mid, mod, usn, tags, flds, sfld,
            csum, flags, data from notes"""):
            # usn: syncing related, ignore.
            # sfld: sorting field, ignore.
            # csum: checksum, ignore.
            # flags: seems empty, ignore.
            # data: seems empty, ignore.
            # Make compatible with openSM2sync:
            guid = guid.replace("`", "ap").replace("\"", "qu")
            guid = guid.replace("&", "am").replace("<", "lt").replace(">", "gt")
            modification_time_for_nid[id] = mod
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
        # Import logs. This needs to happen before creating the cards,
        # otherwise, the sync protocol will use the scheduling data from the
        # latest repetition log, instead of the correct current one.
        w.set_progress_text(_("Importing logs..."))
        number_of_logs = con.execute("select count() from revlog").fetchone()[0]
        w.set_progress_range(number_of_logs)
        w.set_progress_update_interval(number_of_logs/20)
        for id, cid, usn, ease, ivl, lastIvl, factor, time, type_ in \
            con.execute("""select id, cid, usn, ease, ivl, lastIvl, factor,
            time, type from revlog"""):
            # usn: syncing related, ignore.
            if type_ == 0:  # Acquisition phase.
                grade = 0
            else:  # Retention phase.
                grade = ease + 1  # Anki ease is from 1 to 4.
            timestamp = int(id/1000)
            scheduled_interval = lastIvl*86400 if lastIvl > 0 else 0
            new_interval = ivl*86400 if ivl > 0 else 0
            next_rep = timestamp + new_interval
            easiness = factor/1000 if factor else 2.5
            db.log_repetition(timestamp=timestamp, card_id=cid, grade=grade,
                easiness=easiness, acq_reps=0, ret_reps=0, lapses=0,
                acq_reps_since_lapse=0, ret_reps_since_lapse=0,
                scheduled_interval=scheduled_interval,
                actual_interval=scheduled_interval,
                thinking_time=int(time/1000), next_rep=next_rep,
                scheduler_data=0)
            w.increase_progress(1)
        # Import cards.
        w.set_progress_text(_("Importing cards..."))
        number_of_cards = con.execute("select count() from cards").fetchone()[0]
        w.set_progress_range(number_of_cards)
        w.set_progress_update_interval(number_of_cards/20)
        for id, nid, did, ord, mod, usn, type_, queue, due, ivl, factor, reps, \
            lapses, left, odue, odid, flags, data in con.execute("""select id,
            nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps,
            lapses, left, odue, odid, flags, data from cards"""):
            # type: 0=new, 1=learning, 2=due
            # queue: same as above, and -1=suspended,
            #        -2=user buried, -3=sched buried
            # due is used differently for different queues.
            # - new queue: note id or random int
            # - rev queue: integer day
            # - lrn queue: integer timestamp
            # In Mnemosyne, type=2 / rev queue corresponds to grades >= 2.
            # mod: modification time, but gets updated on each answer.
            # usn: syncing related, ignore.
            # left: repetitions left to graduation, ignore.
            # odue: original due, related to filtered decks, ignore.
            # odid: original deck id, related to filtered decks, ignore.
            # flags: seems empty, ignore.
            # data: seems empty, ignore
            fact = fact_for_nid[nid]
            card_type = card_type_for_nid[nid]
            creation_time = int(nid / 1000)
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
            card.next_rep = collection_creation_time + due*86400
            card.last_rep = card.next_rep - ivl*86400
            card.easiness = factor/1000 if factor else 2.5
            card.acq_reps = 1   # No information.
            card.ret_reps = reps
            card.lapses = lapses
            card.acq_reps_since_lapse = card.acq_reps  # No information.
            card.ret_reps_since_lapse = card.ret_reps  # No information.
            card.modification_time = modification_time_for_nid[nid]
            self.active = (queue >= 0)
            if type_ == 0:  # 'new', unseen.
                card.reset_learning_data()
            elif type_ == 1:  # 'learning', acquisition phase.
                card.grade = 0
                card.last_rep = mod
                card.next_rep = mod
            else:  # 'due', retention phase.
                card.grade = 4  # No information.
            if card.grade >= 2:
                assert card.ret_reps_since_lapse != 0 # Issue #93 on github.
            if already_imported:
                db.update_card(card)
            else:
                db.add_card(card)
            w.increase_progress(1)
        # Create criteria for 'database' tags.
        for deck_name in deck_name_for_did.values():
            deck_name = deck_name.strip().replace(",", ";")
            if deck_name in [criterion.name for criterion in db.criteria()]:
                continue
            tag = tag_with_name[deck_name]
            criterion = DefaultCriterion(\
                component_manager=self.component_manager)
            criterion.name = deck_name
            criterion._tag_ids_active.add(tag._id)
            criterion._tag_ids_forbidden = set()
            db.add_criterion(criterion)
        # Clean up.
        con.close()
        if tmp_dir:
            shutil.rmtree(tmp_dir)
        w.close_progress()
        self.warned_about_missing_media = False
