#
# SQLite_sync.py - Peter Bienstman <Peter.Bienstman@gmail.com>
#                  Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#

import os
import re
import time
import sqlite3

from openSM2sync.log_entry import LogEntry
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.utils import normalise_path, expand_path


re_src = re.compile(r"""(src|data)=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)

# Simple named-tuple like class, to avoid the expensive creation a full card
# object (Python 2.5 does not yet have a named tuple).

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class SQLiteSync(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    Note that we only store events like EDITED_CARD, not the data itself that
    was edited. This is filled out during the actual sync with the latest data
    for that card. This needs special care, e.g. if objects are created and
    immediately destroyed, or if information is needed that only becomes
    available later during the sync protocol. It does however save considerable
    space, and since backing up the file before sync can on some platforms be
    the most time consuming step of the sync, we have chosen this option.

    """

    def append_to_sync_partner_info(self, partner_info):
        return partner_info

    def set_sync_partner_info(self, info):
        self.sync_partner_info = info
        # We also use this function to set some variables at the beginning of
        # the sync process.
        self.reapply_default_criterion_needed = False
        # At the beginning of the sync process, we install a mechanism to make
        # make sure that all card types used during sync can actually be
        # instantiated. This is complicated by the fact that in one sync
        # session, a card can be created, followed by a creation of a new card
        # type, followed by a conversion of that card to that new card type.
        # In this case, the card creation event will already list the new card
        # type, which will only be created later during sync.
        self.card_types_to_instantiate_later = set()

    def partners(self):
        return [cursor[0] for cursor in self.con.execute("""select partner
            from partnerships where partner!=?""", ("log.txt", ))]

    def create_if_needed_partnership_with(self, partner):
        sql_res = self.con.execute("""select partner from partnerships
           where partner=?""", (partner, )).fetchone()
        if not sql_res:
            self.con.execute("""insert into partnerships(partner,
               _last_log_id) values(?,?)""", (partner, 0))

    def remove_partnership_with(self, partner):
        self.con.execute("delete from partnerships where partner=?",
            (partner, ))

    def merge_partners(self, remote_partners):

        """Remember the indirect sync partners. Since we don't need their
        _last_log_id, we set it -1.

        """

        local_partners = self.partners()
        for partner in remote_partners:
            if partner not in local_partners and \
               partner != self.sync_partner_info["machine_id"] and \
               partner != self.config().machine_id():
                self.con.execute("""insert into partnerships(partner,
                     _last_log_id) values(?,?)""", (partner, -1))

    def reset_partnerships(self):

        """Reset partnerships, e.g. after restoring from a backup or after
        doing a full sync. This will make sure that a next sync will be a
        full sync if appropriate.

        """

        self.con.execute(\
            "update partnerships set _last_log_id=? where partner!=?",
            (-666, "log.txt"))

    def is_sync_reset_needed(self, partner):
        return self.last_log_index_synced_for(partner) == -666

    def last_log_index_synced_for(self, partner):
        return self.con.execute("""select _last_log_id from partnerships
           where partner=?""", (partner, )).fetchone()[0]

    def update_last_log_index_synced_for(self, partner):
        # We use this function to do some cleaning up at the end of the sync
        # process as well.
        #
        # At the end of the sync, see if we were able to actually instantiate
        # all card types.
        if len(self.card_types_to_instantiate_later) != 0:
            raise RuntimeError(_("Missing plugins for card types."))
        # See if we need to reapply the default criterion.
        if self.reapply_default_criterion_needed:
            criterion = self.current_criterion()
            applier = self.component_manager.current("criterion_applier",
                used_for=criterion.__class__)
            applier.apply_to_database(criterion)
        # Now we can update the last log index.
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.current_log_index(), partner))

    def number_of_log_entries_to_sync_for(self, partner,
            interested_in_old_reps=True):
        _id = self.last_log_index_synced_for(partner)
        if interested_in_old_reps:
            return self.con.execute("select count() from log where _id>?",
                (_id, )).fetchone()[0]
        else:
            return self.con.execute("""select count() from log where _id>? and
                event_type!=?""", (_id, EventTypes.REPETITION)).fetchone()[0]

    def number_of_log_entries(self, interested_in_old_reps=True):
        if interested_in_old_reps:
            return self.con.execute("select count() from log").fetchone()[0]
        else:
            return self.con.execute("""select count() from log where
                event_type!=?""", (EventTypes.REPETITION,)).fetchone()[0]

    def log_entries_to_sync_for(self, partner, interested_in_old_reps=True):

        """Note that we return an iterator here to be able to stream
        efficiently.

        """

        _id = self.last_log_index_synced_for(partner)
        if interested_in_old_reps:
            return (self._log_entry(cursor) for cursor in self.con.execute(\
                "select * from log where _id>?", (_id, )))
        else:
            return (self._log_entry(cursor) for cursor in self.con.execute(\
                "select * from log where _id>? and event_type!=?",
                (_id, EventTypes.REPETITION)))

    def all_log_entries(self, interested_in_old_reps=True):
        if interested_in_old_reps:
            return (self._log_entry(cursor) for cursor in self.con.execute(\
                "select * from log"))
        else:
            return (self._log_entry(cursor) for cursor in self.con.execute(\
                "select * from log where event_type!=?",
                (EventTypes.REPETITION, )))

    def media_filenames_to_sync_for(self, partner):

        """Determine which media files need to be sent across during the sync.
        Obviously, this only includes existing media files, not deleted ones.

        """

        _id = self.last_log_index_synced_for(partner)
        filenames = set()
        for filename in [cursor[0] for cursor in self.con.execute(\
            """select object_id from log where _id>? and (event_type=? or
            event_type=?)""", (_id, EventTypes.ADDED_MEDIA_FILE,
            EventTypes.EDITED_MEDIA_FILE))]:
            if os.path.exists(\
                normalise_path(expand_path(filename, self.media_dir()))):
                filenames.add(filename)
        return filenames

    def all_media_filenames(self):

        """Determine all media files, for use in the initial full sync."""

        # We cannot rely on logs in the database here, since part of it
        # may have been archived, so we simply send across the entire
        # media directory.

        filenames = set()
        for root, dirs, files in os.walk(self.media_dir()):
            subdir = root.replace(self.media_dir(), "")
            for name in files:
                filename = os.path.join(subdir, name)
                if filename.startswith("\\") or filename.startswith("/"):
                    filename = filename[1:]
                filenames.add(filename)
        return filenames

    def generate_log_entries_for_settings(self):

        """Needed after binary initial upload/download of the database, to
        ensure that the side effects to config get applied.

        """

        for key in self.config().keys_to_sync:
            self.log().edited_setting(key)

    def active_objects_to_export(self):
        active_objects = {}
        # Active facts (working with python sets turns out to be more
        # efficient than a 'distinct' statement in SQL).
        active_objects["_fact_ids"] = list(\
            set([cursor[0] for cursor in self.con.execute(\
            "select _fact_id from cards where active=1")]))
        # Active cards and their inactive sister cards.
        # (We need to log cards too instead of just facts, otherwise we cannot
        # communicate the card type.)
        active_objects["_card_ids"] = \
            [cursor[0] for cursor in self.con.execute(\
            """select _id from cards where _fact_id in
            (select _fact_id from cards where active=1)""")]
        # Tags belonging to the active cards.
        active_objects["tags"] = self.tags_from_cards_with_internal_ids(\
            active_objects["_card_ids"])
        # User defined card types.
        defined_in_database_ids = set([cursor[0] for cursor in \
            self.con.execute("select id from card_types")])
        # Card types of the active cards (no need to include inactive sister
        # cards here, as they share the same card type).
        active_card_type_ids = set([cursor[0] for cursor in self.con.execute(\
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
        # Sort to make sure we add the parents first.
        active_objects["card_type_ids"] = \
            sorted(active_card_type_ids.union(parent_card_type_ids))
        # Fact views.
        active_objects["fact_view_ids"] = []
        for card_type_id in active_objects["card_type_ids"]:
            active_objects["fact_view_ids"] += eval(self.con.execute(\
                "select fact_view_ids from card_types where id=?",
                (card_type_id, )).fetchone()[0])
        # Media files for active cards.
        active_objects["media_filenames"] = self.active_dynamic_media_files()
        for result in self.con.execute(\
            """select value from data_for_fact where _fact_id in (select
            _fact_id from cards where active=1) and value like '%src=%'"""):
            for match in re_src.finditer(result[0]):
                active_objects["media_filenames"].add(match.group(2))
        return active_objects

    def set_extra_tags_on_import(self, tags):
        self.extra_tags_on_import = tags

    def _log_entry(self, sql_res):

        """Create log entry object in the format openSM2sync expects."""

        log_entry = LogEntry()
        log_entry["type"] = sql_res[1]
        log_entry["time"] = sql_res[2]
        o_id = sql_res[3]
        if o_id:
            log_entry["o_id"] = o_id
        event_type = log_entry["type"]
        if event_type in (EventTypes.LOADED_DATABASE,
            EventTypes.SAVED_DATABASE):
            log_entry["sch"] = sql_res[6]
            log_entry["n_mem"] = sql_res[7]
            log_entry["act"] = sql_res[8]
        elif event_type in (EventTypes.ADDED_CARD, EventTypes.EDITED_CARD):
            if self.has_card_with_id(log_entry["o_id"]):
                # Note that some of these values (e.g. the repetition count) we
                # could in theory calculate from the previous state and the
                # grade. However, we send the entire state of the card across
                # because it could be that there is no valid previous state
                # because of conflict resolution.
                # Note that we deliberately do not send across 'active', as
                # this is controlled by the remote client.
                card = self.card(log_entry["o_id"], is_id_internal=False)
                if self.sync_partner_info.get("capabilities") == "cards":
                    log_entry["f"] = card.question("sync_to_card_only_client")
                    log_entry["b"] = card.answer("sync_to_card_only_client")
                else:
                    log_entry["card_t"] = card.card_type.id
                    log_entry["fact"] = card.fact.id
                    log_entry["fact_v"] = card.fact_view.id
                log_entry["c_time"] = card.creation_time
                log_entry["m_time"] = card.modification_time
                log_entry["tags"] = ",".join([tag.id for tag in card.tags])
                log_entry["gr"] = card.grade
                log_entry["e"] = card.easiness
                log_entry["l_rp"] = card.last_rep
                log_entry["n_rp"] = card.next_rep
                log_entry["ac_rp"] = card.acq_reps
                log_entry["rt_rp"] = card.ret_reps
                log_entry["lps"] = card.lapses
                log_entry["ac_rp_l"] = card.acq_reps_since_lapse
                log_entry["rt_rp_l"] = card.ret_reps_since_lapse
                log_entry["sch_data"] = card.scheduler_data
                if card.extra_data:
                    log_entry["extra"] = repr(card.extra_data)
            else: # The object has been deleted at a later stage.
                pass
        elif event_type == EventTypes.REPETITION:
            log_entry["gr"] = sql_res[4]
            log_entry["e"] = sql_res[5]
            log_entry["sch_i"] = sql_res[11]
            log_entry["act_i"] = sql_res[12]
            log_entry["th_t"] = sql_res[13]
            log_entry["ac_rp"] = sql_res[6]
            log_entry["rt_rp"] = sql_res[7]
            log_entry["lps"] = sql_res[8]
            log_entry["ac_rp_l"] = sql_res[9]
            log_entry["rt_rp_l"] = sql_res[10]
            log_entry["n_rp"] = sql_res[14]
            log_entry["sch_data"] = sql_res[15]
        elif event_type in (EventTypes.ADDED_TAG, EventTypes.EDITED_TAG):
            if self.has_tag_with_id(log_entry["o_id"]):
                tag = self.tag(log_entry["o_id"], is_id_internal=False)
                if tag is None:
                    return None
                log_entry["name"] = tag.name
                if tag.extra_data:
                    log_entry["extra"] = repr(tag.extra_data)
            else: # The object has been deleted at a later stage.
                pass
        elif event_type in (EventTypes.ADDED_MEDIA_FILE,
            EventTypes.EDITED_MEDIA_FILE, EventTypes.DELETED_MEDIA_FILE):
            log_entry["fname"] = sql_res[3]
            del log_entry["o_id"]
        elif event_type in (EventTypes.ADDED_FACT, EventTypes.EDITED_FACT):
            if self.sync_partner_info.get("capabilities") == "cards":
                # The accompanying ADDED_CARD and EDITED_CARD events suffice.
                return None
            if self.has_fact_with_id(log_entry["o_id"]):
                fact = self.fact(log_entry["o_id"], is_id_internal=False)
                for fact_key, value in fact.data.items():
                    log_entry[fact_key] = value
            else: # The object has been deleted at a later stage.
                pass
        elif event_type in (EventTypes.ADDED_FACT_VIEW,
            EventTypes.EDITED_FACT_VIEW):
            if self.has_fact_view_with_id(log_entry["o_id"]):
                fact_view = self.fact_view(log_entry["o_id"],
                    is_id_internal=False)
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
        elif event_type in (EventTypes.ADDED_CARD_TYPE,
            EventTypes.EDITED_CARD_TYPE):
            if self.has_card_type_with_id(log_entry["o_id"]):
                card_type = self.card_type(log_entry["o_id"],
                    is_id_internal=False)
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
        elif event_type in (EventTypes.ADDED_CRITERION,
            EventTypes.EDITED_CRITERION):
            if self.has_criterion_with_id(log_entry["o_id"]):
                criterion = self.criterion(log_entry["o_id"],
                    is_id_internal=False)
                log_entry["name"] = criterion.name
                log_entry["criterion_type"] = criterion.criterion_type
                log_entry["data"] = criterion.data_to_sync_string()
        elif event_type == EventTypes.EDITED_SETTING:
            if log_entry["o_id"] not in self.config():  # Obsolete entry.
                return None
            log_entry["value"] = repr(self.config()[log_entry["o_id"]])
        return log_entry

    def add_tag_from_log_entry(self, log_entry):
        already_imported = self.has_tag_with_id(log_entry["o_id"])
        if "name" not in log_entry:
            log_entry["name"] = "dummy"  # Added and immediately deleted.
        same_name_in_database = self.con.execute(\
            "select 1 from tags where name=? and id!=? limit 1",
            (log_entry["name"], log_entry["o_id"])).fetchone() is not None
        if same_name_in_database:
            # Merging with the tag which is already in the database is more
            # difficult, as then the tag links in the cards would need to
            # be updated.
            if self.importing:  # Don't interrupt sync with dialog.
                self.main_widget().show_information(\
        _("Tag '%s' already in database, renaming new tag to '%s (1)'" \
                 % (log_entry["name"], log_entry["name"])))
            log_entry["name"] += " (1)"
        if already_imported and self.importing:
            log_entry["type"] = EventTypes.EDITED_TAG
            return self.update_tag(self.tag_from_log_entry(log_entry))
        self.add_tag(self.tag_from_log_entry(log_entry))

    def tag_from_log_entry(self, log_entry):
        # When deleting, the log entry only contains the tag's id, so we pull
        # the object from the database. This is a bit slower than just filling
        # in harmless missing keys, but it is more robust against future
        # side effects of tag deletion.
        if log_entry["type"] == EventTypes.DELETED_TAG:
            # Work around legacy logs which contain duplicate deletion events.
            if self.has_tag_with_id(log_entry["o_id"]):
                return self.tag(log_entry["o_id"], is_id_internal=False)
            else:
                # Leftover from old bug, should not reoccur.
                self.main_widget().show_information(\
            _("Deleting same tag twice during sync. Inform the developpers."))
                log_entry["name"] = "irrelevant"
                return Tag(log_entry["name"], log_entry["o_id"])
        # If we are creating a tag that will be deleted at a later stage
        # during this sync, we are missing some (irrelevant) information
        # needed to properly create a tag object.
        if "name" not in log_entry:
            log_entry["name"] = "irrelevant"
        # Create tag object.
        tag = Tag(log_entry["name"], log_entry["o_id"])
        if "extra" in log_entry:
            tag.extra_data = eval(log_entry["extra"])
        # Make sure to create _id fields as well, otherwise database
        # operations or their side effects could fail.
        if log_entry["type"] != EventTypes.ADDED_TAG:
            tag._id = self.con.execute("select _id from tags where id=?",
                (tag.id, )).fetchone()[0]
        return tag

    def add_fact_from_log_entry(self, log_entry):
        if self.importing:
            already_imported = self.has_fact_with_id(log_entry["o_id"])
            if already_imported:
                log_entry["type"] = EventTypes.EDITED_FACT
                return self.update_fact(\
                    self.fact_from_log_entry(log_entry))
        self.add_fact(self.fact_from_log_entry(log_entry))

    def fact_from_log_entry(self, log_entry):
        # Work around legacy logs which contain duplicate deletion events.
        # Leftover from old bug, should not reoccur.
        if log_entry["type"] != EventTypes.ADDED_FACT and \
           not self.has_fact_with_id(log_entry["o_id"]):
            self.main_widget().show_information(\
        _("Deleting same fact twice during sync. Inform the developpers."))
            fact = Fact({}, log_entry["o_id"])
            fact._id = -1
            return fact
        # Get fact object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_FACT:
            return self.fact(log_entry["o_id"], is_id_internal=False)
        # Create fact object.
        fact_data = {}
        for key, value in log_entry.items():
            if key not in ["time", "type", "o_id"]:
                fact_data[key] = value
        fact = Fact(fact_data, log_entry["o_id"])
        if log_entry["type"] != EventTypes.ADDED_FACT:
            fact._id = self.con.execute("select _id from facts where id=?",
                (fact.id, )).fetchone()[0]
        return fact

    def add_card_from_log_entry(self, log_entry):
        if self.importing:
            already_imported = self.has_card_with_id(log_entry["o_id"])
            if already_imported:
                orig_card = self.card(log_entry["o_id"], is_id_internal=False)
                card = self.card_from_log_entry(log_entry)
                card.grade = orig_card.grade
                card.easiness = orig_card.easiness
                card.acq_reps = orig_card.acq_reps
                card.ret_reps = orig_card.ret_reps
                card.lapses = orig_card.lapses
                card.acq_reps_since_lapse = orig_card.acq_reps_since_lapse
                card.ret_reps_since_lapse = orig_card.ret_reps_since_lapse
                card.next_rep = orig_card.next_rep
                card.last_rep = orig_card.last_rep
                card.modification_time = int(time.time())
                if "extra" in log_entry:
                    card.extra_data = eval(log_entry["extra"])
                card.tags = orig_card.tags
                for tag_id in log_entry["tags"].split(","):
                    card.tags.add(self.tag(tag_id, is_id_internal=False))
                for tag in self.extra_tags_on_import:
                    card.tags.add(tag)
                card.card_type = self.card_type(\
                    log_entry["card_t"], is_id_internal=False)
                if self.is_user_card_type(card.card_type):
                    card.fact_view = self.fact_view(\
                        log_entry["fact_v"], is_id_internal=False)
                else:
                    for fact_view in card.card_type.fact_views:
                        if fact_view.id == log_entry["fact_v"]:
                            card.fact_view = fact_view
                            break
                return self.update_card(card)
        self.add_card(self.card_from_log_entry(log_entry))

    def card_from_log_entry(self, log_entry):
        # We should not receive cards with question and answer data, only
        # cards based on facts.
        if "f" in log_entry:
            raise AttributeError
        # Get card object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_CARD:
            try:
                return self.card(log_entry["o_id"], is_id_internal=False)
            except MnemosyneError:  # There is no fact in the database.
                # We have created and deleted this card since the last sync,
                # so we just return an empty shell.
                card_type = self.card_type_with_id("1")
                fact = Fact({"f": "f", "b": "b"}, id="")
                card = Card(card_type, fact, card_type.fact_views[0],
                    creation_time=0)
                card._id = None # Signals special case to 'delete_card'.
                card.id = log_entry["o_id"]
                return card
        # Create an empty shell of card object that will be deleted later
        # during this sync.
        if "tags" not in log_entry:
            card_type = self.card_type_with_id("1")
            fact = Fact({"f": "f", "b": "b"}, id="")
            card = Card(card_type, fact, card_type.fact_views[0],
                creation_time=0)
            card.id = log_entry["o_id"]
            return card
        # Create card object.
        if "card_t" not in log_entry:
            # Client only supports simple cards.
            card_type = self.card_type_with_id("1")
        else:
            if log_entry["card_t"] not in \
                self.component_manager.card_type_with_id:
                # If the card type is not in the database, it's possible that
                # the data for this card type will follow later during the
                # sync. In that case, create a dummy card type here, which
                # will be corrected by a later edit event. Hovewer, we still
                # need to instantiate this card type later, so that we can
                # catch errors, e.g. due to bad plugins.
                try:
                    self.activate_plugins_for_card_type_with_id\
                        (log_entry["card_t"])
                    card_type = self.card_type_with_id\
                        (log_entry["card_t"])
                except:
                    self.card_types_to_instantiate_later.add(\
                        log_entry["card_t"])
                    card_type = self.card_type_with_id("1")
                    log_entry["fact_v"] = card_type.fact_views[0].id
            else:
                card_type = self.card_type_with_id(log_entry["card_t"])
        fact = self.fact(log_entry["fact"], is_id_internal=False)
        # When importing, set the creation time to the current time.
        if self.importing and not self.importing_with_learning_data:
            log_entry["c_time"] = int(time.time())
            log_entry["m_time"] = int(time.time())
        for fact_view in card_type.fact_views:
            if fact_view.id == log_entry["fact_v"]:
                card = Card(card_type, fact, fact_view,
                    creation_time=log_entry["c_time"])
                break
        for tag_id in log_entry["tags"].split(","):
            if self.has_tag_with_id(tag_id):
                card.tags.add(self.tag(tag_id, is_id_internal=False))
            else:
                # The tag has been deleted later later during the log. Don't
                # worry about it now, this will be corrected by a later
                # EDITED_CARD event.
                pass
        if self.importing:
            if len(self.extra_tags_on_import) != 0:
                card.tags.discard(\
                    self.tag("__UNTAGGED__", is_id_internal=False))
            for tag in self.extra_tags_on_import:
                card.tags.add(tag)
        # Construct rest of card. The 'active' property does not need to be
        # handled here, as default criterion will be applied to the card
        # in the database functions.
        card.id = log_entry["o_id"]
        if (log_entry["type"] != EventTypes.ADDED_CARD) or self.importing:
            if self.has_card_with_id(card.id):
                card._id = self.con.execute("select _id from cards where id=?",
                    (card.id, )).fetchone()[0]
            else:
                # Importing a card for the first time, so it is not yet in the
                # database.
                pass
        card.modification_time = log_entry["m_time"]
        card.grade = log_entry["gr"]
        card.easiness = log_entry["e"]
        card.acq_reps = log_entry["ac_rp"]
        card.ret_reps = log_entry["rt_rp"]
        card.lapses = log_entry["lps"]
        card.acq_reps_since_lapse = log_entry["ac_rp_l"]
        card.ret_reps_since_lapse = log_entry["rt_rp_l"]
        card.last_rep = log_entry["l_rp"]
        card.next_rep = log_entry["n_rp"]
        if "sch_data" in log_entry:
            card.scheduler_data = log_entry["sch_data"]
        if "extra" in log_entry:
            card.extra_data = eval(log_entry["extra"])
        return card

    def apply_repetition(self, log_entry):
        sch_data = log_entry.get("sch_data") # Gives None if not present.
        card = Bunch(id=log_entry["o_id"], grade=log_entry["gr"],
            easiness=log_entry["e"], acq_reps=log_entry["ac_rp"],
            ret_reps=log_entry["rt_rp"], lapses=log_entry["lps"],
            acq_reps_since_lapse=log_entry["ac_rp_l"],
            ret_reps_since_lapse=log_entry["rt_rp_l"],
            last_rep=log_entry["time"], next_rep=log_entry["n_rp"],
            scheduler_data=sch_data)
        self.log().repetition(card, log_entry["sch_i"], log_entry["act_i"],
            log_entry["th_t"])
        self.con.execute("""update cards set grade=?, easiness=?, acq_reps=?,
            ret_reps=?, lapses=?, acq_reps_since_lapse=?,
            ret_reps_since_lapse=?, last_rep=?, next_rep=?, scheduler_data=?
            where id=?""", (card.grade, card.easiness, card.acq_reps,
            card.ret_reps, card.lapses, card.acq_reps_since_lapse,
            card.ret_reps_since_lapse, card.last_rep, card.next_rep,
            card.scheduler_data, card.id))

    def add_media_file(self, log_entry):

        """ADDED_MEDIA_FILE events get created in several places:
        database._process_media, database.check_for_edited_media_files,
        latex, ... . In order to make sure that all of these are treated
        in the same way, we generate an ADDED_MEDIA_FILE event here, and
        prevent _process_media from generating this event through
        self.syncing = True.

        """

        filename = log_entry["fname"]
        full_path = normalise_path(expand_path(filename, self.media_dir()))
        if os.path.exists(full_path):
            self.con.execute("""insert or replace into media(filename, _hash)
                values(?,?)""", (filename, self._media_hash(filename)))
        self.log().added_media_file(filename)

    def edit_media_file(self, log_entry):
        filename = log_entry["fname"]
        self.con.execute("update media set _hash=? where filename=?",
            (self._media_hash(filename), filename))
        self.log().edited_media_file(filename)

    def delete_media_file(self, log_entry):
        # Actually, we cannot take the responsibility to delete a media file,
        # since it would e.g. break the corner case to add a media file,
        # delete it and than add it again.
        pass

        #filename = log_entry["fname"]
        #full_path = expand_path(filename, self.media_dir())
        # The file could have been remotely deleted before it got a chance to
        # be synced, so we need to check if the file exists before deleting.
        #if os.path_exists(full_path):
        #    os.remove(full_path)
        #self.log().deleted_media_file(filename)

    def add_fact_view_from_log_entry(self, log_entry):
        if self.importing:
            already_imported = self.con.execute(\
                "select 1 from fact_views where id=? limit 1",
                (log_entry["o_id"], )).fetchone() is not None
            # No need to rename fact views here, as the user only names the
            # card types.
            if already_imported:
                log_entry["type"] = EventTypes.EDITED_FACT_VIEW
                return self.update_fact_view(\
                    self.fact_view_from_log_entry(log_entry))
        try:
            self.add_fact_view(self.fact_view_from_log_entry(log_entry))
        except sqlite3.IntegrityError:
            # Leftover from old bug, should not reoccur.
            self.main_widget().show_information(\
    _("Creating same fact view twice during sync. Inform the developpers."))

    def fact_view_from_log_entry(self, log_entry):
        # Get fact view object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_FACT_VIEW:
            return self.fact_view(log_entry["o_id"], is_id_internal=False)
        # Create an empty shell of fact view object that will be deleted later
        # during this sync.
        if "name" not in log_entry:
            return FactView("irrelevant", log_entry["o_id"])
        # Create fact view object.
        fact_view = FactView(log_entry["name"], log_entry["o_id"])
        fact_view.q_fact_keys = eval(log_entry["q_fact_keys"])
        fact_view.a_fact_keys = eval(log_entry["a_fact_keys"])
        fact_view.q_fact_key_decorators = eval(log_entry["q_fact_key_decorators"])
        fact_view.a_fact_key_decorators = eval(log_entry["a_fact_key_decorators"])
        fact_view.a_on_top_of_q = bool(eval(log_entry["a_on_top_of_q"]))
        fact_view.type_answer = bool(eval(log_entry["type_answer"]))
        if "extra" in log_entry:
            fact_view.extra_data = eval(log_entry["extra"])
        return fact_view

    def add_card_type_from_log_entry(self, log_entry):
        already_imported = self.con.execute(\
            "select 1 from card_types where id=? limit 1",
            (log_entry["o_id"], )).fetchone() is not None
        if "name" not in log_entry:
            log_entry["name"] = "dummy"  # Added and immediately deleted.
        same_name_in_database = self.con.execute(\
            "select 1 from card_types where name=? and id!=? limit 1",
            (log_entry["name"], log_entry["o_id"] )).fetchone() is not None
        if same_name_in_database:
            # Merging with the card type which is already in the database
            # is more difficult, as then the card type links in the cards
            # would need to be updated.
            if self.importing:  # Don't interrupt sync with dialog.
                self.main_widget().show_information(\
    _("Card type '%s' already in database, renaming new card type to '%s (1)'" \
                % (log_entry["name"], log_entry["name"])))
            log_entry["name"] += " (1)"
        if already_imported and self.importing:
            log_entry["type"] = EventTypes.EDITED_CARD_TYPE
            return self.update_card_type(\
                self.card_type_from_log_entry(log_entry))
        try:
            card_type = self.card_type_from_log_entry(log_entry)
            self.activate_plugins_for_card_type_with_id(card_type.id)
            self.add_card_type(card_type)
        except sqlite3.IntegrityError:
            # Leftover from old bug, should not reoccur.
            self.main_widget().show_information(\
    _("Creating same card type twice during sync. Inform the developpers."))

    def card_type_from_log_entry(self, log_entry):
        # Get card type object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_CARD_TYPE:
            return self.card_type(log_entry["o_id"], is_id_internal=False)
        # Create an empty shell of card type object that will be deleted later
        # during this sync.
        if "fact_views" not in log_entry:
            card_type = CardType(self.component_manager)
            card_type.id = log_entry["o_id"]
            card_type.fact_views = []
            card_type.fact_keys_and_names = []
            return card_type
        # Create card type object.
        card_type = CardType(self.component_manager)
        card_type.id = log_entry["o_id"]
        card_type.name = log_entry["name"]
        card_type.fact_keys_and_names = eval(log_entry["fact_keys_and_names"])
        card_type.fact_views = []
        for fact_view_id in eval(log_entry["fact_views"]):
            card_type.fact_views.append(self.fact_view(fact_view_id,
                is_id_internal=False))
        card_type.unique_fact_keys = eval(log_entry["unique_fact_keys"])
        card_type.required_fact_keys = eval(log_entry["required_fact_keys"])
        card_type.keyboard_shortcuts = eval(log_entry["keyboard_shortcuts"])
        if "extra" in log_entry:
            card_type.extra_data = eval(log_entry["extra"])
        return card_type

    def criterion_from_log_entry(self, log_entry):
        # Get criterion object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_CRITERION:
            return self.criterion(log_entry["o_id"], is_id_internal=False)
        # Create an empty shell of criterion object that will be deleted later
        # during this sync.
        if "criterion_type" not in log_entry:
            from mnemosyne.libmnemosyne.criteria.default_criterion \
                 import DefaultCriterion
            return DefaultCriterion(self.component_manager, log_entry["o_id"])
        # Create criterion object.
        for criterion_class in self.component_manager.all("criterion"):
            if criterion_class.criterion_type == log_entry["criterion_type"]:
                criterion = \
                    criterion_class(self.component_manager, log_entry["o_id"])
                criterion.name = log_entry["name"]
                # Try to apply the data to the criterion. If this fails, it
                # means that the data to do this is not yet available at this
                # stage of the sync, and will be corrected by a later
                # EDITED_CRITERION event.
                try:
                    criterion.set_data_from_sync_string(log_entry["data"])
                except TypeError:
                    pass
        if log_entry["type"] != EventTypes.ADDED_CRITERION:
            criterion._id = self.con.execute("""select _id from criteria where
                id=?""", (criterion.id, )).fetchone()[0]
        return criterion

    def apply_log_entry(self, log_entry, importing=False):
        if not importing:
            self.syncing = True
        else:
            self.importing = True
        event_type = log_entry["type"]
        if "time" in log_entry:
            self.log().timestamp = int(log_entry["time"])
        # TMP measure to allow syncing partners which did not yet store
        # machine ids for LOADED_DATABASE and SAVED_DATABASE.
        if not "o_id" in log_entry:
            log_entry["o_id"] = ""
        try:
            if event_type == EventTypes.STARTED_PROGRAM:
                self.log().started_program(log_entry["o_id"])
            elif event_type == EventTypes.STOPPED_PROGRAM:
                self.log().stopped_program()
            elif event_type == EventTypes.STARTED_SCHEDULER:
                self.log().started_scheduler(log_entry["o_id"])
            elif event_type == EventTypes.LOADED_DATABASE:
                self.log().loaded_database(log_entry["o_id"], log_entry["sch"],
                    log_entry["n_mem"], log_entry["act"])
            elif event_type == EventTypes.SAVED_DATABASE:
                self.log().saved_database(log_entry["o_id"], log_entry["sch"],
                    log_entry["n_mem"], log_entry["act"])
            elif event_type == EventTypes.ADDED_TAG:
                self.add_tag_from_log_entry(log_entry)
            elif event_type == EventTypes.EDITED_TAG:
                self.update_tag(self.tag_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_TAG:
                self.delete_tag(self.tag_from_log_entry(log_entry))
            elif event_type == EventTypes.ADDED_FACT:
                self.add_fact_from_log_entry(log_entry)
            elif event_type == EventTypes.EDITED_FACT:
                self.update_fact(self.fact_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_FACT:
                self.delete_fact(self.fact_from_log_entry(log_entry))
            elif event_type == EventTypes.ADDED_CARD:
                self.add_card_from_log_entry(log_entry)
            elif event_type == EventTypes.EDITED_CARD:
                self.update_card(self.card_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_CARD:
                self.delete_card(self.card_from_log_entry(log_entry))
            elif event_type == EventTypes.REPETITION:
                self.apply_repetition(log_entry)
            elif event_type == EventTypes.ADDED_MEDIA_FILE:
                self.add_media_file(log_entry)
            elif event_type == EventTypes.EDITED_MEDIA_FILE:
                self.edit_media_file(log_entry)
            elif event_type == EventTypes.DELETED_MEDIA_FILE:
                self.delete_media_file(log_entry)
            elif event_type == EventTypes.ADDED_FACT_VIEW:
                self.add_fact_view_from_log_entry(log_entry)
            elif event_type == EventTypes.EDITED_FACT_VIEW:
                self.update_fact_view(self.fact_view_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_FACT_VIEW:
                self.delete_fact_view(self.fact_view_from_log_entry(log_entry))
            elif event_type == EventTypes.ADDED_CARD_TYPE:
                self.add_card_type_from_log_entry(log_entry)
                self.card_types_to_instantiate_later.discard(log_entry["o_id"])
            elif event_type == EventTypes.EDITED_CARD_TYPE:
                self.update_card_type(self.card_type_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_CARD_TYPE:
                self.delete_card_type(self.card_type_from_log_entry(log_entry))
            elif event_type == EventTypes.ADDED_CRITERION:
                self.add_criterion(self.criterion_from_log_entry(log_entry))
            elif event_type == EventTypes.EDITED_CRITERION:
                criterion = self.criterion_from_log_entry(log_entry)
                self.update_criterion(criterion)
                if criterion.id == "__DEFAULT__":
                    self.reapply_default_criterion_needed = True
            elif event_type == EventTypes.DELETED_CRITERION:
                self.delete_criterion(self.criterion_from_log_entry(log_entry))
            elif event_type == EventTypes.EDITED_SETTING:
                key, value = log_entry["o_id"], eval(log_entry["value"])
                if key in self.config().keys_to_sync:
                    self.config()[key] = value
                    for card_type in self.card_types():
                        for render_chain in self.component_manager.\
                            all("render_chain"):
                            render_chain.renderer_for_card_type(card_type).\
                                update(card_type)
                else:
                    self.log_edited_setting(log_entry["time"], key)
        finally:
            self.log().timestamp = None
            self.syncing = False
            self.importing = False
