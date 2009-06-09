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
    UPLOADED = 15
    UPLOAD_FAILED = 16
    STOPPED_PROGRAM = 17
                            
    def started_program(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.STARTED_PROGRAM, int(time.time()), "Mnemosyne %s %s %s" % \
             (mnemosyne.version.version, os.name, sys.platform)))

    def started_scheduler(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
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
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.ADDED_FACT, int(time.time()), fact._id))
        
    def updated_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_FACT, int(time.time()), fact._id))
        
    def deleted_fact(self, fact):
        # For deleted objects, we store the id as opposed to the _id, as there
        # is no way to retrieve it afterwards.
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.DELETED_FACT, int(time.time()), fact.id))
        
    def added_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.ADDED_TAG, int(time.time()), tag._id))
        
    def updated_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_TAG, int(time.time()), tag._id))
        
    def deleted_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.DELETED_TAG, int(time.time()), tag.id))
        
    def added_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.ADDED_CARD, int(time.time()), card._id))
        
    def updated_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_CARD, int(time.time()), card._id))
        
    def deleted_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.DELETED_CARD, int(time.time()), card.id))
        
    def repetition(self, card, scheduled_interval, actual_interval, \
                   new_interval, noise=0):
        self.database().con.execute(\
            """insert into history(event, timestamp, _object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (self.REPETITION, int(time.time()), card._id, card.grade,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            scheduled_interval, actual_interval, new_interval,
            int(stopwatch.time())))

    def uploaded(self, filename):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPLOADED, int(time.time()), filename))
        
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
        index = int(sql_res["_last_history_id"])
        # Loop over history entries and dump them to text file.
        # Make sure to convert _id's to id's when needed.
        for cursor in self.database().con.execute(\
            "select * from history where _id>?", (index, )):
            event = cursor["event"]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(cursor["timestamp"]))
            if event == self.STARTED_PROGRAM:
                print >> logfile, "%s : Program started : %s" \
                      % (timestamp, cursor["_object_id"])
            elif event == self.STARTED_SCHEDULER:
                print >> logfile, "%s : Scheduler : %s" \
                      % (timestamp, cursor["_object_id"])
            elif event == self.LOADED_DATABASE:
                print >> logfile, "%s : Loaded database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])                              
            elif event == self.SAVED_DATABASE:
                print >> logfile, "%s : Saved database %d %d %d" \
                      % (timestamp, cursor["acq_reps"], cursor["ret_reps"],
                         cursor["lapses"])
            elif event == self.ADDED_CARD:
                sql_res = self.database().con.execute(\
                    "select id from cards where _id=?",
                    (cursor["_object_id"], )).fetchone()
                # Use dummy grade and interval, We log the first repetition
                # separately anyhow.
                print >> logfile, "%s : New item %s -1 -1" \
                      % (timestamp, sql_res["id"])
            elif event == self.DELETED_CARD:
                print >> logfile, "%s : Deleted item %s" \
                      % (timestamp, cursor["_object_id"])


            elif event == self.STOPPED_PROGRAM:
                print >> logfile, "%s : Program stopped" % (timestamp, )
                
        # Update partnership index.
