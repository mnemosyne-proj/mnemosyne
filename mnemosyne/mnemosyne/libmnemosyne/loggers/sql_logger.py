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
            (self.ADDED_FACT, int(time.time()), fact.id))
        
    def updated_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_FACT, int(time.time()), fact.id))
        
    def deleted_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.DELETED_FACT, int(time.time()), fact.id))
        
    def added_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.ADDED_TAG, int(time.time()), tag.id))
        
    def updated_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_TAG, int(time.time()), tag.id))
        
    def deleted_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.DELETED_TAG, int(time.time()), tag.id))
        
    def new_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.ADDED_CARD, int(time.time()), card.id))
        
    def updated_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            (self.UPDATED_CARD, int(time.time()), card.id))
        
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
            (self.REPETITION, int(time.time()), card.id, card.grade,
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
