#
# SQLite_sync.py - Max Usachev <maxusachev@gmail.com>
#                  Ed Bartosh <bartosh@gmail.com>
#                  Peter Bienstman <Peter.Bienstman@UGent.be>
#

from openSM2sync.log_event import EventCodes as Event


class SQLiteSync(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """
    
    def create_partnership_if_needed(self, partner):
        sql_res = self.con.execute("""select partner from partnerships 
           where partner=?""", (partner, )).fetchone()
        if not sql_res:
            self.con.execute("""insert into partnerships(partner, 
               _last_log_id) values(?,?)""", (partner, 0))
            
    def get_history_log_entries(self, partner):
        _id = self.get_last_sync_log_entry(partner)
        return self.con.execute("""select event, timestamp, object_id,
           scheduled_interval, actual_interval, new_interval, thinking_time
           from log where _id>%s""" % _id).fetchall()
    
    def get_media_history_log_entries(self, partner):
        _id = self.get_last_sync_log_entry(partner)
        return self.con.execute("""select event, object_id from log where
           _id>? and event in (?,?)""", (_id, Event.ADDED_MEDIA, \
           Event.DELETED_MEDIA)).fetchall()

    def number_of_log_entries_to_sync_for(self, partner):
        _id = self.get_last_sync_log_entry(partner)
        return self.con.execute("""select count() from log where
           _id>? and event in (?,?,?,?,?,?,?,?)""", (_id, Event.ADDED_FACT, \
           Event.UPDATED_FACT, Event.DELETED_FACT, Event.ADDED_TAG, \
           Event.UPDATED_TAG, Event.ADDED_CARD, Event.UPDATED_CARD, \
           Event.REPETITION)).fetchone()[0]

    def number_of_media_to_sync_for(self, partner):
        _id = self.get_last_sync_log_entry(partner)
        return self.con.execute("""select count() from log where 
           _id>? and event=?""", (_id, Event.ADDED_MEDIA)).fetchone()[0]
 
    def get_last_sync_log_entry(self, partner):
        sql_res = self.con.execute("""select _last_log_id from partnerships 
           where partner=?""", (partner, )).fetchone()
        return sql_res["_last_log_id"]
 
    def update_last_sync_log_entry(self, partner):
        _id = self.con.execute("""select _id from log""").fetchall()[-1][0]
        self.con.execute("""update partnerships set _last_log_id=? 
           where partner=?""", (_id, partner))
            
