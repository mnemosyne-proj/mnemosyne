#
# SQLite_sync.py - Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#                  Peter Bienstman <Peter.Bienstman@UGent.be>
#

from openSM2sync.log_event import LogEvent
from openSM2sync.log_event import EventTypes


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
        
        for attr in ("event_type", "timestamp", "object_id"):
            setattr(log_event, attr, sql_res[attr])
        log_event.data = {}
        if log_event.event_type == EventTypes.REPETITION:
            for attr in ("grade", "easiness", "acq_reps", "ret_reps", "lapses",
                "acq_reps_since_lapse", "ret_reps_since_lapse",
                "scheduled_interval", "actual_interval", "new_interval",
                "thinking_time"):
                setattr(log_event.data, attr, sql_res[attr])      
    
    def get_log_entries_to_sync_for(self, partner):

        """Note that we return an iterator here to be able to stream
        efficiently.

        """
        
        _id = self.get_last_synced_log_entry_for(partner)
        return (_log_entry(cursor) for cursor in self.con.execute(\
            "select * from log where _id>?", (_id, )))

    def get_last_log_entry_index(self):
        return self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()[0]
    
    def update_last_sync_log_entry_for(self, partner):
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.get_last_log_entry_index(), partner))
