#
# SQLite_sync.py - Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#                  Peter Bienstman <Peter.Bienstman@UGent.be>
#

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

    def get_last_synced_log_entry_for(self, partner):
        sql_res = self.con.execute("""select _last_log_id from partnerships 
           where partner=?""", (partner, )).fetchone()
        return sql_res["_last_log_id"]
    
    def number_of_log_entries_to_sync_for(self, partner):
        _id = self.get_last_synced_log_entry_for(partner)
        return self.con.execute("select count() from log where _id>?",
            (_id, )).fetchone()[0]

    def _log_entry(self, sql_res):

        """Create log entry object in the form openSM2sync expects."""

        log_entry = LogEntry()
        for attr in ("event_type", "timestamp", "object_id"):
            setattr(log_entry, attr, sql_res[attr])
        log_entry.data = {}
        event_type = log_entry.event_type
        if event_type in (EventTypes.ADDED_TAG, EventTypes.UPDATED_TAG):
            tag = self.get_tag(log_entry.object_id, id_is_internal=False)
            log_entry.data["name"] = tag.name
        if event_type == EventTypes.REPETITION:
            for attr in ("grade", "easiness", "acq_reps", "ret_reps", "lapses",
                "acq_reps_since_lapse", "ret_reps_since_lapse",
                "scheduled_interval", "actual_interval", "new_interval",
                "thinking_time"):
                setattr(log_entry.data, attr, sql_res[attr])
        return log_entry
    
    def get_log_entries_to_sync_for(self, partner):

        """Note that we return an iterator here to be able to stream
        efficiently.

        """
        
        _id = self.get_last_synced_log_entry_for(partner)
        return (self._log_entry(cursor) for cursor in self.con.execute(\
            "select * from log where _id>?", (_id, )))

    def apply_log_entry(self, log_entry):
        if log_entry.event_type == EventTypes.ADDED_TAG:
            tag = Tag(log_entry.data["name"], log_entry.object_id)
            self.add_tag(tag, log_entry.timestamp)
            
        return
        
        if log_entry == EventTypes.ADDED_FACT:
            fact = self.create_fact_object(child)
            self.database.add_fact(fact)
        elif log_entry == EventTypes.UPDATED_FACT:
            fact = self.database.get_fact(child.find("id").text, False)
            if fact:
                self.database.update_fact(self.create_fact_object(child))
            else:
                self.allow_update_card = False
        elif log_entry == EventTypes.DELETED_FACT:
            fact = self.database.get_fact(child.find("id").text, False)
            if fact:
                self.database.delete_fact_and_related_data(fact)
        elif log_entry == EventTypes.ADDED_TAG:
            tag = self.create_tag_object(child)
            if not tag.name in self.database.get_tag_names():
                self.database.add_tag(tag)
        elif log_entry == EventTypes.UPDATED_TAG:
            self.database.update_tag(self.create_tag_object(child))
        elif log_entry == EventTypes.ADDED_CARD:
            card = self.create_card_object(child)
            self.database.add_card(card)
            self.database.log_added_card(int(child.find("tm").text), card.id)
        elif log_entry == EventTypes.UPDATED_CARD:
            if self.allow_update_card:
                self.database.update_card(self.create_card_object(child))
            self.allow_update_card = True
        elif log_entry == EventTypes.REPETITION:
            old_card = self.database.get_card(child.find("id").text, False)
            new_card = self.create_card_object(child)
            if new_card.timestamp > old_card.last_rep:
                self.database.update_card(new_card)
                self.database.log_repetition(new_card.timestamp, \
                new_card.id, new_card.grade, new_card.easiness, \
                new_card.acq_reps, new_card.ret_reps, new_card.lapses, \
                new_card.acq_reps_since_lapse, \
                new_card.ret_reps_since_lapse, new_card.scheduled_interval,\
                new_card.actual_interval, new_card.new_interval, \
                new_card.thinking_time)
                
    def get_last_log_entry_index(self):
        return self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()[0]
    
    def update_last_sync_log_entry_for(self, partner):
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.get_last_log_entry_index(), partner))
