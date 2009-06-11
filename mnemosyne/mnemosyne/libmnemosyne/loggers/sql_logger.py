#
# sql_logger.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time

import mnemosyne.version
from mnemosyne.libmnemosyne.logger import Logger
from mnemosyne.libmnemosyne.stopwatch import stopwatch


class SqlLogger(Logger):

    STARTED_PROGRAM = 1
    STARTED_SCHEDULER = 2
    LOADED_DATABASE = 3
    SAVED_DATABASE = 4
    ADDED_FACT = 5
    UPDATED_FACT = 6
    DELETED_FACT = 7
    ADDED_TAG = 8
    UPDATED_TAG = 9
    DELETED_TAG = 10
    ADDED_CARD = 11
    UPDATED_CARD = 12
    DELETED_CARD = 13
    REPETITION = 14
    UPLOADED_LOG = 15
    UPLOAD_FAILED = 16
    STOPPED_PROGRAM = 17
                            
    def started_program(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.STARTED_PROGRAM, int(time.time()), "Mnemosyne %s %s %s" % \
             (mnemosyne.version.version, os.name, sys.platform)))

    def started_scheduler(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.STARTED_SCHEDULER, int(time.time()), self.scheduler().name))
    
    def loaded_database(self):
        sch = self.scheduler()
        self.database().con.execute(\
            """insert into history(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (self.LOADED_DATABASE, int(time.time()), sch.scheduled_count(),
            sch.non_memorised_count(), sch.active_count()))
        
    def saved_database(self):
        sch = self.scheduler()
        self.database().con.execute(\
            """insert into history(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            (self.SAVED_DATABASE, int(time.time()), sch.scheduled_count(),
            sch.non_memorised_count(), sch.active_count()))
        
    def added_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_FACT, int(time.time()), fact.id))
        
    def updated_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_FACT, int(time.time()), fact.id))
        
    def deleted_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_FACT, int(time.time()), fact.id))
        
    def added_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_TAG, int(time.time()), tag.id))
        
    def updated_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_TAG, int(time.time()), tag.id))
        
    def deleted_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_TAG, int(time.time()), tag.id))
        
    def added_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.ADDED_CARD, int(time.time()), card.id))
        
    def updated_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.UPDATED_CARD, int(time.time()), card.id))
        
    def deleted_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.DELETED_CARD, int(time.time()), card.id))
        
    def repetition(self, card, scheduled_interval, actual_interval, \
                   new_interval, noise=0):
        self.database().con.execute(\
            """insert into history(event, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.REPETITION, int(time.time()), card.id, card.grade,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            scheduled_interval, actual_interval, new_interval,
            int(stopwatch.time())))

    def uploaded_log(self, filename):
        self.database().con.execute(\
            "insert into history(event, timestamp, object_id) values(?,?,?)",
            (self.UPLOADED_LOG, int(time.time()), filename))
        
    def upload_failed(self):
        self.database().con.execute(\
            "insert into history(event, timestamp) values(?,?)",
            (self.UPLOAD_FAILED, int(time.time())))
        
    def stopped_program(self):
        self.database().con.execute(\
            "insert into history(event, timestamp) values(?,?)",
            (self.STOPPED_PROGRAM, int(time.time())))

    def dump_to_txt_log(self):
        # Open log file and get starting index.
        logname = os.path.join(self.config().basedir, "log.txt")
        logfile = file(logname, "a")
        sql_res = self.database().con.execute(\
            "select _last_history_id from partnerships where partner=?",
            ("log.txt", )).fetchone()
        last_index = int(sql_res["_last_history_id"])
        index = 0
        # Loop over history entries and dump them to text file.
        for cursor in self.database().con.execute(\
            "select * from history where _id>?", (last_index, )):
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
            elif event == self.UPLOADED_LOG:
                print >> logfile, "%s : Uploaded %s" %\
                      (timestamp, cursor["object_id"])
            elif event == self.UPLOAD_FAILED:
                print >> logfile, "%s : Upload failed" % (timestamp, )
            elif event == self.STOPPED_PROGRAM:
                print >> logfile, "%s : Program stopped" % (timestamp, )               
        # Update partnership index.
        self.database().con.execute(\
            "update partnerships set _last_history_id=? where partner=?",
            (index, "log.txt"))
