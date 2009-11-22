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
        if event_type in (EventTypes.LOADED_DATABASE,
           EventTypes.SAVED_DATABASE):
            log_entry.data["sch"] = sql_res["acq_reps"]
            log_entry.data["n_mem"] = sql_res["ret_reps"]
            log_entry.data["act"] = sql_res["lapses"]            
        elif event_type in (EventTypes.ADDED_TAG, EventTypes.UPDATED_TAG):
            tag = self.get_tag(log_entry.object_id, id_is_internal=False)
            log_entry.data["name"] = tag.name
        elif event_type == EventTypes.REPETITION:
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
        event_type = log_entry.event_type
        if event_type in (EventTypes.STARTED_PROGRAM,
           EventTypes.STOPPED_PROGRAM, EventTypes.STARTED_SCHEDULER):
            self.con.execute("""insert into log(event_type, timestamp,
               object_id) values(?,?,?)""", (event_type, log_entry.timestamp,
               log_entry.object_id))
        elif event_type in (EventTypes.LOADED_DATABASE,
           EventTypes.SAVED_DATABASE):
            self.con.execute("""insert into log(event_type, timestamp,
            acq_reps, ret_reps, lapses) values(?,?,?,?,?)""", (event_type,
            log_entry.timestamp, log_entry.data["sch"],
            log_entry.data["n_mem"], log_entry.data["act"]))
        elif event_type == EventTypes.ADDED_TAG:
            tag = Tag(log_entry.data["name"], log_entry.object_id)
            self.add_tag(tag, log_entry.timestamp)
                
    def get_last_log_entry_index(self):
        return self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()[0]
    
    def update_last_sync_log_entry_for(self, partner):
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.get_last_log_entry_index(), partner))
