#
# parse_logs.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import sqlite3

from openSM2sync.log_event import EventCodes as Event
from mnemosyne.libmnemosyne.file_formats.science_log_parser \
     import ScienceLogParser


SCHEMA = """
    begin;
          
    create table log(
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
                
    create table _cards(
        id text primary key,
        last_rep int,
        offset int
    );

    create table parsed_logs(
        log_name text primary key
    );
    
    commit;
"""


class LogDatabase(object):

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self._connection = None
        db_name = os.path.join(self.log_dir, "logs.db")
        initialisation_needed = not os.path.exists(db_name)
        self.con = sqlite3.connect(db_name, timeout=0.1,
                                   isolation_level="EXCLUSIVE")
        self.con.row_factory = sqlite3.Row
        if initialisation_needed:
            self.con.executescript(SCHEMA)

    def parse_directory(self):       
        self.parser = ScienceLogParser(database=self)
        self._delete_indices()  # Takes too long while parsing.
        filenames = [os.path.join(self.log_dir, filename) for filename in \
            sorted(os.listdir(unicode(self.log_dir))) if \
            filename.endswith(".bz2")]
        filenames_count = len(filenames)
        for counter, filename in enumerate(filenames):
            sys.stdout.flush()
            if self.con.execute(\
                "select log_name from parsed_logs where parsed_logs.log_name=?",
                (os.path.basename(filename), )).fetchone() is not None:
                print "(%d/%d) %1.1f%% %s already parsed" % \
                      (counter + 1, filenames_count,
                      (counter + 1.) / filenames_count * 100, \
                      os.path.basename(filename))
                continue
            print "(%d/%d) %1.1f%% %s" % (counter + 1, filenames_count,
                (counter + 1.) / filenames_count * 100, \
                os.path.basename(filename))
            try:
                self.parser.parse(filename)
            except KeyboardInterrupt:                                              
                print "Interrupted!"
                exit()
            except:
                print "Can't open file, ignoring."
            self.con.execute("insert into parsed_logs(log_name) values(?)",
                (os.path.basename(filename), ))
            self.con.commit()
        self._create_indices()

    def _delete_indices(self):
        self.con.execute("drop index if exists i_log_timestamp;")
        self.con.execute("drop index if exists i_log_user_id;")
        self.con.execute("drop index if exists i_log_object_id;")
        
    def _create_indices(self):
        self.con.execute("create index i_log_timestamp on log (timestamp);")
        self.con.execute("create index i_log_user_id on log (user_id);")
        self.con.execute("create index i_log_object_id on log (object_id);")
                                         
    def log_started_program(self, timestamp, program_name_version):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.parser.user_id, Event.STARTED_PROGRAM, int(timestamp),
             program_name_version)) 

    def log_stopped_program(self, timestamp):
        self.con.execute(\
            "insert into log(user_id, event, timestamp) values(?,?,?)",
            (self.parser.user_id, Event.STOPPED_PROGRAM, int(timestamp)))

    def log_started_scheduler(self, timestamp, scheduler_name):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.parser.user_id, Event.STARTED_SCHEDULER, int(timestamp),
            scheduler_name))
    
    def log_loaded_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?,?)""",
            (self.parser.user_id, Event.LOADED_DATABASE, int(timestamp),
            scheduled_count, non_memorised_count, active_count))
        
    def log_saved_database(self, timestamp, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?,?)""",
            (self.parser.user_id, Event.SAVED_DATABASE, int(timestamp),
            scheduled_count, non_memorised_count, active_count))
        
    def log_added_card(self, timestamp, card_id):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.parser.user_id, Event.ADDED_CARD, int(timestamp), card_id))
        
    def log_deleted_card(self, timestamp, card_id):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id)
            values(?,?,?,?)""",
            (self.parser.user_id, Event.DELETED_CARD, int(timestamp), card_id))
     
    def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
        ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval, new_interval, thinking_time):
        self.con.execute(\
            """insert into log(user_id, event, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.parser.user_id, Event.REPETITION, int(timestamp), card_id,
            grade, easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, int(thinking_time)))

    def set_offset_last_rep(self, card_id, offset, last_rep):
        self.con.execute(\
            """insert or replace into _cards(id, offset, last_rep)
            values(?,?,?)""",
            (card_id + self.parser.user_id, offset, int(last_rep)))

    def get_offset_last_rep(self, card_id):
        sql_result = self.con.execute("""select offset, last_rep
           from _cards where _cards.id=?""",
           (card_id + self.parser.user_id, )).fetchone()
        return sql_result["offset"], sql_result["last_rep"]
    
    def update_card_after_log_import(self, id, creation_time, offset):
        pass

if __name__=="__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <log_directory>" % sys.argv[0]
    else:
        LogDatabase(log_dir=sys.argv[1]).parse_directory()

