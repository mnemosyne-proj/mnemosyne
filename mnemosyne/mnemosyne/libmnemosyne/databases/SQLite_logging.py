#
# SQLite_logging.py <Peter.Bienstman@UGent.be>
#

import os
import time


class SQLiteLogging(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    The interface here is a bit low level, as it needs to serve both for
    logging when the program is running and for manipulating the log when
    doing a sync or importing pre-2.0 logs. (A higher level interface for the
    former use case is in logging.sql_logger.)

    """

    STARTED_PROGRAM = 1
    STOPPED_PROGRAM = 2
    STARTED_SCHEDULER = 3
    LOADED_DATABASE = 4
    SAVED_DATABASE = 5
    ADDED_TAG = 6
    UPDATED_TAG = 7
    DELETED_TAG = 8
    ADDED_FACT = 9
    UPDATED_FACT = 10
    DELETED_FACT = 11
    ADDED_CARD = 12
    UPDATED_CARD = 13
    DELETED_CARD = 14
    ADDED_CARD_TYPE = 15
    UPDATED_CARD_TYPE = 16
    DELETED_CARD_TYPE = 17
    REPETITION = 18
    ADDED_MEDIA = 19
    DELETED_MEDIA = 20
                            
    def log_started_program(self, timestamp, program_name_version):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.STARTED_PROGRAM, int(timestamp), program_name_version)) 

    def log_stopped_program(self, timestamp):
        self.con.execute(\
            "insert into log(event, timestamp) values(?,?)",
            (self.STOPPED_PROGRAM, int(timestamp)))

    def log_started_scheduler(self, timestamp, scheduler_name):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.STARTED_SCHEDULER, int(timestamp), scheduler_name))
    
    def log_loaded_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (self.LOADED_DATABASE, int(timestamp), scheduled_count,
            non_memorised_count, active_count))
        
    def log_saved_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (self.SAVED_DATABASE, int(timestamp), scheduled_count,
            non_memorised_count, active_count))
        
    def log_added_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_TAG, int(timestamp), tag_id))
        
    def log_updated_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_TAG, int(timestamp), tag_id))
        
    def log_deleted_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_TAG, int(timestamp), tag_id))
        
    def log_added_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_FACT, int(timestamp), fact_id))
        
    def log_updated_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_FACT, int(timestamp), fact_id))
        
    def log_deleted_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_FACT, int(timestamp), fact_id))
        
    def log_added_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_CARD, int(timestamp), card_id))
        
    def log_updated_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_CARD, int(timestamp), card_id))
        
    def log_deleted_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_CARD, int(timestamp), card_id))
        
    def log_added_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_updated_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_deleted_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_CARD_TYPE, int(timestamp), card_type_id))
        
    def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
        ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval, new_interval, thinking_time):
        self.con.execute(\
            """insert into log(event, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.REPETITION, int(timestamp), card_id, grade, easiness,
            acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, int(thinking_time)))

    def log_added_media(self, timestamp, filename, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_MEDIA, int(timestamp),
             filename + "__for__" + fact_id))       

    def log_deleted_media(self, timestamp, filename, fact_id):
        self.con.execute(\
            "insert into log(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_MEDIA, int(timestamp),
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
            if event == self.STARTED_PROGRAM:
                print >> logfile, "%s : Program started : %s" \
                      % (timestamp, cursor["object_id"])
            elif event == self.STARTED_SCHEDULER:
                print >> logfile, "%s : Scheduler : %s" \
                      % (timestamp, cursor["object_id"])
            elif event == self.LOADED_DATABASE:
                print >> logfile, "%s : Loaded database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])                              
            elif event == self.SAVED_DATABASE:
                print >> logfile, "%s : Saved database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])
            elif event == self.ADDED_CARD:
                # Use dummy grade and interval, We log the first repetition
                # separately anyhow.
                print >> logfile, "%s : New item %s -1 -1" \
                      % (timestamp, cursor["object_id"])
            elif event == self.DELETED_CARD:
                print >> logfile, "%s : Deleted item %s" \
                      % (timestamp, cursor["object_id"])
            elif event == self.REPETITION:
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
            elif event == self.STOPPED_PROGRAM:
                print >> logfile, "%s : Program stopped" % (timestamp, )               
        # Update partnership index.
        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (index, "log.txt"))

    # The following functions are only used when importing pre-2.0 logs.
    # They are needed to store temporary data about cards whis is used during
    # the parsing process.

    def create_temp_import_tables(self):
        if not self.con.execute("pragma table_info(cards_data)").fetchall():
            self.con.execute("""create temp table _cards(
                id text primary key,
                last_rep_time int,
                offset int);""")

    def set_offset_last_rep_time(self, card_id, offset, last_rep_time):
        self.con.execute(\
            """insert or replace into _cards(id, offset, last_rep_time)
            values(?,?,?)""", (card_id, offset, int(last_rep_time)))

    def get_offset_last_rep_time(self, card_id):
        sql_result = self.con.execute("""select offset, last_rep_time
           from _cards where _cards.id=?""", (card_id, )).fetchone()
        return sql_result["offset"], sql_result["last_rep_time"]
