#
# SQLite_logging.py <Peter.Bienstman@UGent.be>
#

import os
import time

from openSM2sync.log_event import EventCodes as Event


class SQLiteLogging(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    The interface here is a bit low level, as it needs to serve both for
    logging when the program is running and for manipulating the log when
    doing a sync or importing pre-2.0 logs. (A higher level interface for the
    former use case is in logging.sql_logger.)

    """
                            
    def log_started_program(self, timestamp, program_name_version):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.STARTED_PROGRAM, int(timestamp), program_name_version)) 

    def log_stopped_program(self, timestamp):
        self.con.execute(\
            "insert into log(event, timestamp) values(?,?)",
            (Event.STOPPED_PROGRAM, int(timestamp)))

    def log_started_scheduler(self, timestamp, scheduler_name):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.STARTED_SCHEDULER, int(timestamp), scheduler_name))
    
    def log_loaded_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (Event.LOADED_DATABASE, int(timestamp), scheduled_count,
            non_memorised_count, active_count))
        
    def log_saved_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (Event.SAVED_DATABASE, int(timestamp), scheduled_count,
            non_memorised_count, active_count))
        
    def log_added_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.ADDED_TAG, int(timestamp), tag_id))
        
    def log_updated_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.UPDATED_TAG, int(timestamp), tag_id))
        
    def log_deleted_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.DELETED_TAG, int(timestamp), tag_id))
        
    def log_added_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.ADDED_FACT, int(timestamp), fact_id))
        
    def log_updated_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.UPDATED_FACT, int(timestamp), fact_id))
        
    def log_deleted_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.DELETED_FACT, int(timestamp), fact_id))
        
    def log_added_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.ADDED_CARD, int(timestamp), card_id))
        
    def log_updated_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.UPDATED_CARD, int(timestamp), card_id))
        
    def log_deleted_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.DELETED_CARD, int(timestamp), card_id))
        
    def log_added_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.ADDED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_updated_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.UPDATED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_deleted_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.DELETED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
        ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval, new_interval, thinking_time):
        self.con.execute(\
            """insert into log(event, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (Event.REPETITION, int(timestamp), card_id, grade, easiness,
            acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, int(thinking_time)))

    def log_added_media(self, timestamp, filename, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.ADDED_MEDIA, int(timestamp),
             filename + "__for__" + fact_id))       

    def log_deleted_media(self, timestamp, filename, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (Event.DELETED_MEDIA, int(timestamp),
             filename + "__for__" + fact_id))
    
    def dump_to_txt_log(self):
        # Open log file and get starting index.
        logname = os.path.join(self.config().basedir, "log.txt")
        logfile = file(logname, "a")
        sql_res = self.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()
        last_index = int(sql_res["_last_log_id"])
        index = 0
        # Loop over log entries and dump them to text file.
        for cursor in self.con.execute(\
            "select * from log where _id>?", (last_index, )):
            index = int(cursor["_id"])
            event = cursor["event"]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(cursor["timestamp"]))
            if event == Event.STARTED_PROGRAM:
                print >> logfile, "%s : Program started : %s" \
                      % (timestamp, cursor["object_id"])
            elif event == Event.STARTED_SCHEDULER:
                print >> logfile, "%s : Scheduler : %s" \
                      % (timestamp, cursor["object_id"])
            elif event == Event.LOADED_DATABASE:
                print >> logfile, "%s : Loaded database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])                              
            elif event == Event.SAVED_DATABASE:
                print >> logfile, "%s : Saved database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])
            elif event == Event.ADDED_CARD:
                # Use dummy grade and interval, We log the first repetition
                # separately anyhow.
                print >> logfile, "%s : New item %s -1 -1" \
                      % (timestamp, cursor["object_id"])
            elif event == Event.DELETED_CARD:
                print >> logfile, "%s : Deleted item %s" \
                      % (timestamp, cursor["object_id"])
            elif event == Event.REPETITION:
                print >> logfile, \
              "%s : R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f" %\
                         (timestamp, cursor["object_id"], cursor["grade"],
                          cursor["easiness"], cursor["acq_reps"],
                          cursor["ret_reps"], cursor["lapses"],
                          cursor["acq_reps_since_lapse"],
                          cursor["ret_reps_since_lapse"],
                          cursor["scheduled_interval"],
                          cursor["actual_interval"], cursor["new_interval"],
                          0, cursor["thinking_time"])
            elif event == Event.STOPPED_PROGRAM:
                print >> logfile, "%s : Program stopped" % (timestamp, )               
        # Update partnership index.
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (index, "log.txt"))

    # The following functions are only used when importing pre-2.0 cards and
    # logs. They are needed to store temporary data about cards whis is used
    # during the parsing process.

    def before_mem_import(self):
        if not self.con.execute("pragma table_info(cards_data)").fetchall():
            self.con.execute("""create temp table _cards(
                id text primary key,
                offset int,
                last_rep int);""")
        # This is a useful index to have when importing.
        self.con.execute("create index i_cards_id on cards (id);")
        # Having these indices in place while importing takes too long.
        self.con.execute("drop index if exists i_log_timestamp;")
        self.con.execute("drop index if exists i_log_object_id;")

    def after_mem_import(self):
        self.con.execute("drop table _cards")
        # Restore index situation.
        self.con.execute("drop index i_cards_id;")
        self.con.execute("create index i_log_timestamp on log (timestamp);")
        self.con.execute("create index i_log_object_id on log (object_id);")

    def set_offset_last_rep(self, card_id, offset, last_rep):
        self.con.execute(\
            """insert or replace into _cards(id, offset, last_rep)
            values(?,?,?)""", (card_id, offset, int(last_rep)))

    def get_offset_last_rep(self, card_id):
        sql_res = self.con.execute("""select offset, last_rep
           from _cards where _cards.id=?""", (card_id, )).fetchone()
        return sql_res["offset"], sql_res["last_rep"]

    def update_card_after_log_import(self, id, creation_time, offset):
        sql_res = self.con.execute("""select _id, _fact_id, acq_reps,
            lapses, acq_reps_since_lapse from cards where id=?""",
            (id, )).fetchone()
        acq_reps = sql_res["acq_reps"] + offset
        acq_reps_since_lapse = sql_res["acq_reps_since_lapse"]
        if sql_res["lapses"] == 0:
            acq_reps_since_lapse += offset
        self.con.execute("""update cards set acq_reps=?,
            acq_reps_since_lapse=? where _id=?""",
            (acq_reps, acq_reps_since_lapse, sql_res["_id"]))
        self.con.execute("""update facts set creation_time=?,
            modification_time=? where _id=?""",
            (creation_time, creation_time, sql_res["_fact_id"]))

    def get_log_index(self):
        return self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()[0]

    def remove_added_card_events_since(self, index):
        self.con.execute("delete from log where _id>? and event=?",
            (index, Event.ADDED_CARD))
        self.con.execute("vacuum")
        
    def bring_txt_log_partnership_index_forward(self):
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.get_log_index(), "log.txt"))       
