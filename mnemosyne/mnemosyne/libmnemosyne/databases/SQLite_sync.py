#
# SQLite_sync.py - Peter Bienstman <Peter.Bienstman@UGent.be>
#                  Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#

import os
import time

from openSM2sync.log_entry import LogEntry
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.filters.latex import Latex

# Simple named-tuple like class, to avoid the expensive creation a full card
# object. (Python 2.5 does not yet have a named tuple.)

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class SQLiteSync(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """

    def set_sync_partner_info(self, info):
        self.sync_partner_info = info
    
    def create_partnership_if_needed_for(self, partner):
        # Needed? could be folded in pre sync merge partnerships?
        sql_res = self.con.execute("""select partner from partnerships 
           where partner=?""", (partner, )).fetchone()
        if not sql_res:
            self.con.execute("""insert into partnerships(partner, 
               _last_log_id) values(?,?)""", (partner, 0))

    # TODO: delete?
    def partnerships_old(self):
        partnerships = {}
        for sql_res in self.con.execute("""select * from partnerships where
            partner!=?""", ("log.txt", )):
            partnerships[sql_res["partner"]] = sql_res["_last_log_id"]
        return partnerships
    
    def partners(self):
        return [cursor[0] for cursor in self.con.execute("""select partner
            from partnerships where partner!=?""", ("log.txt", ))]

    def merge_partnerships_before_sync(self, remote_partnerships):
        return

    def last_log_index_synced_for(self, partner):
        return self.con.execute("""select _last_log_id from partnerships 
           where partner=?""", (partner, )).fetchone()[0]

    def update_last_log_index_synced_for(self, partner):
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
        
    def check_for_updated_media_files(self):
        # Regular media files.
        new_hashes = {}
        for sql_res in self.con.execute("select * from media"):
            filename = sql_res["filename"]
            if not os.path.exists(expand_path(filename, self.mediadir())):
                continue
            new_hash = self._media_hash(filename)
            if sql_res["_hash"] != new_hash:
                new_hashes[filename] = new_hash
        for filename, new_hash in new_hashes.iteritems():
            self.con.execute("update media set _hash=? where filename=?",
                (new_hash, filename))
            self.log().updated_media(filename)
        # Latex files (takes 0.10 sec on 8000 card database).
        latex = Latex(self.component_manager)
        for cursor in self.con.execute("select value from data_for_fact"):
            latex.run(cursor[0])
            
    def media_filenames_to_sync_for(self, partner):    
        # Note that Mnemosyne does not delete media files on its own, so
        # DELETED_MEDIA log entries are irrelevant/ignored.
        # We do have to make sure we don't return any files that have been
        # deleted, though.
        _id = self.last_log_index_synced_for(partner)
        filenames = []
        for filename in [cursor[0] for cursor in self.con.execute(\
            """select object_id from log where _id>? and (event_type=? or
            event_type=?)""", (_id, EventTypes.ADDED_MEDIA,
            EventTypes.UPDATED_MEDIA))]:
            if os.path.exists(expand_path(filename, self.mediadir())):
                filenames.append(filename)
        return filenames
        
    def _log_entry(self, sql_res):

        """Create log entry object in the format openSM2sync expects."""

        log_entry = LogEntry()
        log_entry["type"] = sql_res["event_type"]
        log_entry["time"] = sql_res["timestamp"]
        o_id = sql_res["object_id"]
        if o_id:
            log_entry["o_id"] = o_id        
        event_type = log_entry["type"]
        if event_type in (EventTypes.LOADED_DATABASE,
            EventTypes.SAVED_DATABASE):
            log_entry["sch"] = sql_res["acq_reps"]
            log_entry["n_mem"] = sql_res["ret_reps"]
            log_entry["act"] = sql_res["lapses"]            
        elif event_type in (EventTypes.ADDED_TAG, EventTypes.UPDATED_TAG):
            try:
                tag = self.get_tag(log_entry["o_id"], id_is_internal=False)
                log_entry["name"] = tag.name
                if tag.extra_data:
                    log_entry["extra"] = repr(tag.extra_data)
            except TypeError: # The object has been deleted at a later stage.
                pass
        elif event_type in (EventTypes.ADDED_FACT, EventTypes.UPDATED_FACT):
            if self.sync_partner_info.get("capabilities") == "cards":
                # The accompanying ADDED_CARD and UPDATED_CARD events suffice.
                return None
            try:
                fact = self.get_fact(log_entry["o_id"], id_is_internal=False)
                log_entry["c_time"] = fact.creation_time
                log_entry["m_time"] = fact.modification_time
                log_entry["card_t"] = fact.card_type.id
                for key, value in fact.data.iteritems():
                    log_entry[key] = value
            except TypeError: # The object has been deleted at a later stage.
                pass
        elif event_type in (EventTypes.ADDED_CARD, EventTypes.UPDATED_CARD):
            try:
                # Note that some of these values (e.g. the repetition count) we
                # could in theory calculate from the previous state and the
                # grade. However, we send the entire state of the card across
                # because it could be that there is no valid previous state
                # because of conflict resolution.
                card = self.get_card(log_entry["o_id"], id_is_internal=False)
                if self.sync_partner_info.get("capabilities") == "cards":
                    log_entry["q"] = card.question(exporting=True)
                    log_entry["a"] = card.answer(exporting=True)
                else:
                    log_entry["fact"] = card.fact.id
                    log_entry["fact_v"] = card.fact_view.id
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
            except TypeError: # The object has been deleted at a later stage.
                pass
        elif event_type in (EventTypes.ADDED_CARD_TYPE,
            EventTypes.UPDATED_CARD_TYPE, EventTypes.DELETED_CARD_TYPE):
            raise NotImplementedError
        elif event_type == EventTypes.REPETITION:
            log_entry["gr"] = sql_res["grade"]
            log_entry["e"] = sql_res["easiness"]
            log_entry["sch_i"] = sql_res["scheduled_interval"]
            log_entry["act_i"] = sql_res["actual_interval"]
            log_entry["new_i"] = sql_res["new_interval"]
            log_entry["th_t"] = sql_res["thinking_time"]
            log_entry["ac_rp"] = sql_res["acq_reps"]
            log_entry["rt_rp"] = sql_res["ret_reps"]
            log_entry["lps"] = sql_res["lapses"]
            log_entry["ac_rp_l"] = sql_res["acq_reps_since_lapse"]
            log_entry["rt_rp_l"] = sql_res["ret_reps_since_lapse"]
            log_entry["l_rp"] = sql_res["last_rep"]
            log_entry["n_rp"] = sql_res["next_rep"]
            log_entry["sch_data"] = sql_res["scheduler_data"]
        elif event_type in (EventTypes.ADDED_MEDIA, EventTypes.UPDATED_MEDIA,
            EventTypes.DELETED_MEDIA):
            log_entry["fname"] = sql_res["object_id"]
            del log_entry["o_id"]
        return log_entry

    def tag_from_log_entry(self, log_entry):
        # When deleting, the log entry only contains the tag's id, so we pull
        # the object from the database. This is a bit slower than just filling
        # in harmless missing fields, but it is more robust against future
        # side effects of tag deletion.
        if log_entry["type"] == EventTypes.DELETED_TAG:
            return self.get_tag(log_entry["o_id"], id_is_internal=False)
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
    
    def fact_from_log_entry(self, log_entry):
        # Get fact object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_FACT:
            return self.get_fact(log_entry["o_id"], id_is_internal=False)
        # Make sure we can create a fact object that will be deleted later
        # during this sync.
        if "card_t" not in log_entry:
            log_entry["card_t"] = "1"
            log_entry["c_time"] = "-1"
            log_entry["m_time"] = "-1"
        # Create fact object.
        data = {}
        for key, value in log_entry.iteritems():
            if key not in ["time", "type", "o_id", "c_time", "m_time",
                "card_t"]:
                data[key] = value
        card_type = self.card_type_by_id(log_entry["card_t"])
        fact = Fact(data, card_type, log_entry["c_time"], log_entry["o_id"])
        fact.modification_time = log_entry["m_time"]
        if log_entry["type"] != EventTypes.ADDED_FACT:
            fact._id = self.con.execute("select _id from facts where id=?",
                (fact.id, )).fetchone()[0]
        return fact
    
    def card_from_log_entry(self, log_entry):
        # We should not receive cards with question and answer data, only
        # cards based on facts.
        if "q" in log_entry:
            raise AttributeError
        # Get card object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_CARD:
            try:
                # More future-proof version of code in the except statement.
                # However, this will fail if after the last sync the other
                # partner created and deleted this card, so that there is no
                # fact information.
                return self.get_card(log_entry["o_id"], id_is_internal=False)
            except TypeError:
                # Less future-proof version which just returns an empty shell.
                # Make sure to set _id, though, as that will be used in
                # actually deleting the card.
                sql_res = self.con.execute("select * from cards where id=?",
                    (log_entry["o_id"], )).fetchone()
                card_type = self.card_type_by_id("1")
                fact = Fact({}, card_type, creation_time=0, id="")
                card = Card(fact, card_type.fact_views[0])
                card._id = sql_res["_id"]
                return card
        # Create an empty shell of card object that will be deleted later
        # during this sync.
        if "tags" not in log_entry:
            card_type = self.card_type_by_id("1")
            fact = Fact({}, card_type, creation_time=0, id="")
            card = Card(fact, card_type.fact_views[0])
            card.id = log_entry["o_id"]
            return card
        # Create card object.
        fact = self.get_fact(log_entry["fact"], id_is_internal=False)
        for fact_view in fact.card_type.fact_views:
            if fact_view.id == log_entry["fact_v"]:
                card = Card(fact, fact_view)
                break
        for tag_id in log_entry["tags"].split(","):
            try:
                card.tags.add(self.get_tag(tag_id, id_is_internal=False))
            except TypeError:
                # The tag has been later later during the log. Don't worry
                # about it now, this will be corrected by a later
                # UPDATED_CARD event.
                pass
        card.id = log_entry["o_id"]
        if log_entry["type"] != EventTypes.ADDED_CARD:
            card._id = self.con.execute("select _id from cards where id=?",
                (card.id, )).fetchone()[0]      
        card.active = True
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
        if "sch_data" in log_entry:
            sch_data = log_entry["sch_data"]
        else:
            sch_data = None
        card = Bunch(id=log_entry["o_id"], grade=log_entry["gr"],
            easiness=log_entry["e"], acq_reps=log_entry["ac_rp"],
            ret_reps=log_entry["rt_rp"], lapses=log_entry["lps"],
            acq_reps_since_lapse=log_entry["ac_rp_l"],
            ret_reps_since_lapse=log_entry["rt_rp_l"],
            last_rep=log_entry["l_rp"], next_rep=log_entry["n_rp"],
            scheduler_data=sch_data)
        self.log().repetition(card, log_entry["sch_i"], log_entry["act_i"],
                   log_entry["new_i"], log_entry["th_t"])
        self.con.execute("""update cards set grade=?, easiness=?, acq_reps=?,
            ret_reps=?, lapses=?, acq_reps_since_lapse=?,
            ret_reps_since_lapse=?, last_rep=?, next_rep=?, scheduler_data=?
            where id=?""", (card.grade, card.easiness, card.acq_reps,
            card.ret_reps, card.lapses, card.acq_reps_since_lapse,
            card.ret_reps_since_lapse, card.last_rep, card.next_rep,
            card.scheduler_data, card.id))
        
    def add_media(self, log_entry):

        """ADDED_MEDIA events get created in several places:
        database._process_media, database.check_for_updated_media_files,
        latex, ... . In order to make sure that all of these are treated
        in the same way, we generate an ADDED_MEDIA event here, and prevent
        _process_media from generating this event through self.syncing = True.

        """
        
        filename = log_entry["fname"]
        if os.path.exists(expand_path(filename, self.mediadir())):
            self.con.execute("""insert or replace into media(filename, _hash)
                values(?,?)""", (filename, self._media_hash(filename)))
        self.log().added_media(filename)
        
    def update_media(self, log_entry):
        filename = log_entry["fname"]
        self.log().updated_media(filename)
        self.con.execute("update media set _hash=? where filename=?",
            (self._media_hash(filename), filename))
    
    def apply_log_entry(self, log_entry):
        self.syncing = True
        event_type = log_entry["type"]
        self.log().timestamp = int(log_entry["time"])
        try:
            if event_type == EventTypes.STARTED_PROGRAM:
                self.log().started_program(log_entry["o_id"])
            elif event_type == EventTypes.STOPPED_PROGRAM:
                self.log().stopped_program()
            elif event_type == EventTypes.STARTED_SCHEDULER:
                self.log().started_scheduler(log_entry["o_id"])
            elif event_type == EventTypes.LOADED_DATABASE:
                self.log().loaded_database(log_entry["sch"],
                    log_entry["n_mem"], log_entry["act"])
            elif event_type == EventTypes.SAVED_DATABASE:
                self.log().saved_database(log_entry["sch"],
                    log_entry["n_mem"], log_entry["act"])
            elif event_type == EventTypes.ADDED_TAG:
                self.add_tag(self.tag_from_log_entry(log_entry))
            elif event_type == EventTypes.UPDATED_TAG:
                self.update_tag(self.tag_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_TAG:
                self.delete_tag(self.tag_from_log_entry(log_entry))
            elif event_type == EventTypes.ADDED_FACT:
                self.add_fact(self.fact_from_log_entry(log_entry))
            elif event_type == EventTypes.UPDATED_FACT:
                self.update_fact(self.fact_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_FACT:
                fact = self.fact_from_log_entry(log_entry)
                self.delete_fact_and_related_data(fact)
            elif event_type == EventTypes.ADDED_CARD:
                card = self.card_from_log_entry(log_entry)
                # 'add_card' does not log, so we need to do it ourselves.
                self.add_card(card)
                self.log().added_card(card)
            elif event_type == EventTypes.UPDATED_CARD:
                self.update_card(self.card_from_log_entry(log_entry))
            elif event_type == EventTypes.DELETED_CARD:
                self.delete_card(self.card_from_log_entry(log_entry))
            elif event_type == EventTypes.REPETITION:
                self.apply_repetition(log_entry)
            elif event_type == EventTypes.ADDED_MEDIA:
                self.add_media(log_entry)
            elif event_type == EventTypes.UPDATED_MEDIA:
                self.update_media(log_entry)
        finally:
            self.log().timestamp = None
            self.syncing = False
            
