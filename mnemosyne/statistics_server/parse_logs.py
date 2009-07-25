#
# parse_logs.py <Peter.Bienstman@UGent.be>
#

import os
import sqlite3

from mnemosyne.libmnemosyne.loggers.txt_log_parser import TxtLogParser


SCHEMA = """
    begin;
          
    create table log(
        _id integer primary key,
        user_id text,
        event integer,
        timestamp integer,
        object_id text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        scheduled_interval integer,
        actual_interval integer,
        new_interval integer,
        thinking_time integer
    );
    create index i_log on log (timestamp);
    
    create table _cards(
        id text primary key,
        user_id text,
        last_rep_time int,
        offset int
    );
    
    commit;
"""


class LogDatabase(object):
    
    log_dir = "/home/pbienst/mnemosyne_logs"
    
    def __init__(self):
        self._connection = None

    @property
    def con(self):
        
        """Connection to the database, lazily created."""

        if not self._connection:
            db_name = os.path.join(self.log_dir, "logs.db")
            self._connection = sqlite3.connect(db_name, timeout=0.1,
                               isolation_level="EXCLUSIVE")
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def new(self):
        self.con.executescript(SCHEMA)

    # TODO: import this from somewhere?
    
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
    
    def parsing_started(self, user_id, log_number):
        self.user_id = user_id
        # TODO: save log number
                                         
    def log_started_program(self, timestamp, program_name_version):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.user_id, self.STARTED_PROGRAM, int(timestamp),
             program_name_version)) 

    def log_stopped_program(self, timestamp):
        self.con.execute(\
            "insert into log(user_id, event, timestamp) values(?,?,?)",
            (self.user_id, self.STOPPED_PROGRAM, int(timestamp)))

    def log_started_scheduler(self, timestamp, scheduler_name):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.user_id, self.STARTED_SCHEDULER, int(timestamp),
            scheduler_name))
    
    def log_loaded_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?,?)""",
            (self.user_id, self.LOADED_DATABASE, int(timestamp),
            scheduled_count, non_memorised_count, active_count))
        
    def log_saved_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?,?)""",
            (self.user_id, self.SAVED_DATABASE, int(timestamp),
            scheduled_count, non_memorised_count, active_count))
        
    def log_added_card(self, timestamp, card_id):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.user_id, self.ADDED_CARD, int(timestamp), card_id))
        
    def log_deleted_card(self, timestamp, card_id):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.user_id, self.DELETED_CARD, int(timestamp), card_id))        
     
    def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
        ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval, new_interval, thinking_time):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.user_id, self.REPETITION, int(timestamp), card_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, int(thinking_time)))

    def parsing_stopped(self, user_id, log_number):
        pass

    def set_offset_last_rep_time(self, card_id, offset, last_rep_time):
        self.con.execute(\
            """insert or replace into _cards(id, user_id, offset,
            last_rep_time) values(?,?,?,?)""",
            (card_id, self.user_id, offset, int(last_rep_time)))

    def get_offset_last_rep_time(self, card_id):
        sql_result = self.con.execute("""select offset, last_rep_time
           from _cards where _cards.id=? and _cards.user_id=?""",
           (card_id, self.user_id)).fetchone()
        return sql_result["offset"], sql_result["last_rep_time"]

    def parse(self):
        for filename in sorted(os.listdir(self.log_dir)):
            filename = os.path.join(self.log_dir, filename)
            print filename
            if filename.endswith(".bz2"):
                parser = TxtLogParser(filename, self)
                parser.parse()
                self.con.commit()



log_database = LogDatabase()
log_database.new()
log_database.parse()                        
