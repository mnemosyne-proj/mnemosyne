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
                            
    def program_started(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("PS", int(time.time()), "Mnemosyne %s %s %s" % \
             (mnemosyne.version.version, os.name, sys.platform)))

    def scheduler_started(self):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("SS", int(time.time()), self.scheduler().name))
    
    def loaded_database(self):
        sch = self.scheduler()
        self.database().con.execute(\
            """insert into history(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            ("LD", int(time.time()), sch.scheduled_count(), \
            sch.non_memorised_count(), sch.active_count()))
        
    def saved_database(self):
        sch = self.scheduler()
        self.database().con.execute(\
            """insert into history(event, timestamp, acq_reps, ret_reps,
            lapses) values(?,?,?,?,?)""",
            ("SD", int(time.time()), sch.scheduled_count(), \
            sch.non_memorised_count(), sch.active_count()))
        
    def new_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("NF", int(time.time()), fact.id))
        
    def edited_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("EF", int(time.time()), fact.id))
        
    def deleted_fact(self, fact):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("DF", int(time.time()), fact.id))
        
    def new_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("NT", int(time.time()), tag.id))
        
    def edited_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("ET", int(time.time()), tag.id))
        
    def deleted_tag(self, tag):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("DT", int(time.time()), tag.id))
        
    def new_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("NC", int(time.time()), card.id))
        
    def edited_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("EC", int(time.time()), card.id))
        
    def deleted_card(self, card):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("DC", int(time.time()), card.id))
        
    def revision(self, card, scheduled_interval, actual_interval, \
                 new_interval, noise=0):
        self.database().con.execute(\
            """insert into history(event, timestamp, _object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            new_interval, thinking_time)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("R", int(time.time()), card.id, card.grade, card.easiness,
            card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            scheduled_interval, actual_interval, new_interval,
            int(stopwatch.time())))

    def uploaded(self, filename):
        self.database().con.execute(\
            "insert into history(event, timestamp, _object_id) values(?,?,?)",
            ("U", int(time.time()), filename))
        
    def uploading_failed(self):
        self.database().con.execute(\
            "insert into history(event, timestamp) values(?,?)",
            ("UF", int(time.time())))
        
    def program_quit(self):
        self.database().con.execute(\
            "insert into history(event, timestamp) values(?,?)",
            ("PQ", int(time.time())))
