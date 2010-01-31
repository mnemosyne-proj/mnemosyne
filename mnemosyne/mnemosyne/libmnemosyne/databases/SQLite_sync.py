#
# SQLite_sync.py - Peter Bienstman <Peter.Bienstman@UGent.be>
#                  Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#

import time

from openSM2sync.log_entry import LogEntry
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class SQLiteSync(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """
    
    def create_partnership_if_needed_for(self, partner):
        sql_res = self.con.execute("""select partner from partnerships 
           where partner=?""", (partner, )).fetchone()
        if not sql_res:
            self.con.execute("""insert into partnerships(partner, 
               _last_log_id) values(?,?)""", (partner, 0))

    def last_synced_log_entry_for(self, partner):
        sql_res = self.con.execute("""select _last_log_id from partnerships 
           where partner=?""", (partner, )).fetchone()
        return sql_res["_last_log_id"]
    
    def number_of_log_entries_to_sync_for(self, partner):
        _id = self.last_synced_log_entry_for(partner)
        return self.con.execute("select count() from log where _id>?",
            (_id, )).fetchone()[0]

    def check_for_updated_media_files(self):
        new_hashes = {}
        for sql_res in self.con.execute("select * from media"):
            new_hash = self._media_hash(sql_res["filename"])
            if sql_res["_hash"] != new_hash:
                new_hashes[sql_res["filename"]] = new_hash
        for filename, new_hash in new_hashes.iteritems():
            self.con.execute("update media set _hash=? where filename=?",
                (new_hash, filename))
            self.log().updated_media(filename)
            
    def media_filenames_to_sync_for(self, partner):        
        # Note that Mnemosyne does not delete media files on its own, so
        # DELETED_MEDIA log entries are irrelevant/ignored.
        _id = self.last_synced_log_entry_for(partner)
        return [cursor[0] for cursor in self.con.execute("""select object_id
            from log where _id>? and (event_type=? or event_type=?)""",
            (_id, EventTypes.ADDED_MEDIA, EventTypes.UPDATED_MEDIA))]
        
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
                log_entry["fact"] = card.fact.id
                log_entry["fact_v"] = card.fact_view.id
                log_entry["tags"] = ",".join([tag.id for tag in card.tags]) 
                log_entry["act"] = int(card.active)
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
        elif event_type in (EventTypes.ADDED_MEDIA, EventTypes.UPDATED_MEDIA,
            EventTypes.DELETED_MEDIA):
            log_entry["fname"] = sql_res["object_id"]
            del log_entry["o_id"]
        return log_entry
        
    def log_entries_to_sync_for(self, partner):

        """Note that we return an iterator here to be able to stream
        efficiently.

        """
        
        _id = self.last_synced_log_entry_for(partner)
        return (self._log_entry(cursor) for cursor in self.con.execute(\
            "select * from log where _id>?", (_id, )))

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
        # Get card object to be deleted now.
        if log_entry["type"] == EventTypes.DELETED_CARD:
            try:
                # More future-proof version of code in the except stamement.
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
            card.tags.add(self.get_tag(tag_id, id_is_internal=False))
        card.active = bool(log_entry["act"])
        card.grade = log_entry["gr"]
        card.easiness = log_entry["e"]
        card.last_rep = log_entry["l_rp"]
        card.next_rep = log_entry["n_rp"]
        card.acq_reps = log_entry["ac_rp"]
        card.ret_reps = log_entry["rt_rp"]
        card.lapses = log_entry["lps"]
        card.acq_reps_since_lapse = log_entry["ac_rp_l"]
        card.ret_reps_since_lapse = log_entry["rt_rp_l"]
        if "sch_data" in log_entry:
            card.scheduler_data = log_entry["sch_data"]   
        if "extra" in log_entry:
            card.extra_data = eval(log_entry["extra"])
        if log_entry["type"] != EventTypes.ADDED_CARD:
            card._id = self.con.execute("select _id from cards where id=?",
                (card.id, )).fetchone()[0]
        return card

    def apply_repetition(self, log_entry):
        # Note that the corresponding changing of the card properties is
        # handled by a separate UPDATED_CARD event.
        self.log_repetition(log_entry["time"], log_entry["o_id"],
            log_entry["gr"], log_entry["e"], log_entry["ac_rp"],
            log_entry["rt_rp"], log_entry["lps"], log_entry["ac_rp_l"],
            log_entry["rt_rp_l"], log_entry["sch_i"], log_entry["act_i"],
            log_entry["new_i"], log_entry["th_t"])

    def update_media(self, log_entry):
        filename = log_entry["fname"]
        self.con.execute("update media set _hash=? where filename=?",
            (self._media_hash(filename), filename))
        self.log().updated_media(filename)
    
    def apply_log_entry(self, log_entry):
        event_type = log_entry["type"]
        self.log().timestamp = int(log_entry["time"])
        if event_type == EventTypes.STARTED_PROGRAM:
            self.log().started_program(log_entry["o_id"])
        elif event_type == EventTypes.STOPPED_PROGRAM:
            self.log().stopped_program()
        elif event_type == EventTypes.STARTED_SCHEDULER:
            self.log().started_scheduler(log_entry["o_id"])
        elif event_type in (EventTypes.LOADED_DATABASE,
           EventTypes.SAVED_DATABASE):
            self.con.execute("""insert into log(event_type, timestamp,
            acq_reps, ret_reps, lapses) values(?,?,?,?,?)""", (event_type,
            log_entry["time"], log_entry["sch"], log_entry["n_mem"],
            log_entry["act"]))
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
            self.add_card(card) # Does not log, so we need to do it ourselves.
            self.log().added_card(card)
        elif event_type == EventTypes.UPDATED_CARD:
            self.update_card(self.card_from_log_entry(log_entry))
        elif event_type == EventTypes.DELETED_CARD:
            self.delete_card(self.card_from_log_entry(log_entry))
        elif event_type == EventTypes.REPETITION:
            self.apply_repetition(log_entry)
        elif event_type == EventTypes.UPDATED_MEDIA:
            # For ADDED_MEDIA and DELETED_MEDIA events, we don't need to do
            # anything special here. If they are still relevant, they will be
            # taken care of by _process_media. If they are no longer relevant
            # (e.g. adding and subsequently deleting media) they won't make it
            # to the other side, but that's no big deal.
            self.update_media(log_entry)
        self.log().timestamp = None
            
    def last_log_entry_index(self):
        return self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()[0]
    
    def update_last_sync_log_entry_for(self, partner):
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.last_log_entry_index(), partner))
