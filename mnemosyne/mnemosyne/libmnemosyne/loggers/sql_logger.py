#
# sql_logger.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time

import mnemosyne.version
from mnemosyne.libmnemosyne.logger import Logger


class SqlLogger(Logger):
                          
    def started_program(self):
        version_string = "Mnemosyne %s %s %s" % \
             (mnemosyne.version.version, os.name, sys.platform)
        self.database().log_started_program(time.time(), version_string)
        
    def stopped_program(self):
        self.database().log_stopped_program(time.time())
        
    def started_scheduler(self):
        self.database().log_started_scheduler(time.time(),
            self.scheduler().name)
            
    def loaded_database(self):
        sch = self.scheduler()
        self.database().log_loaded_database(time.time(), sch.scheduled_count(),
            sch.non_memorised_count(), sch.active_count())
        
    def saved_database(self):
        sch = self.scheduler()
        self.database().log_saved_database(time.time(), sch.scheduled_count(),
            sch.non_memorised_count(), sch.active_count())
        
    def added_tag(self, tag):
        self.database().log_added_tag(time.time(), tag.id)
        
    def updated_tag(self, tag):
        self.database().log_updated_tag(time.time(), tag.id)
                
    def deleted_tag(self, tag):
        self.database().log_deleted_tag(time.time(), tag.id)
                
    def added_fact(self, fact):
        self.database().log_added_fact(time.time(), fact.id)
        
    def updated_fact(self, fact):
        self.database().log_updated_fact(time.time(), fact.id)
        
    def deleted_fact(self, fact):
        self.database().log_deleted_fact(time.time(), fact.id)
                
    def added_card(self, card):
        self.database().log_added_card(time.time(), card.id)
                
    def updated_card(self, card):
        self.database().log_updated_card(time.time(), card.id)
        
    def deleted_card(self, card):
        self.database().log_deleted_card(time.time(), card.id)
        
    def added_card_type(self, card_type):
        self.database().log_added_card_type(time.time(), card_type.id)
                
    def updated_card_type(self, card_type):
        self.database().log_updated_card_type(time.time(), card_type.id)
        
    def deleted_card_type(self, card_type):
        self.database().log_deleted_card_type(time.time(), card_type.id)
        
    def repetition(self, card, scheduled_interval, actual_interval,
                   new_interval):
        self.database().log_repetition(time.time(), card.id, card.grade,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            scheduled_interval, actual_interval, new_interval,                                              
            self.stopwatch().time())

    def added_media(self, filename, fact):
        self.database().log_added_media(time.time(), filename, fact.id)

    def deleted_media(self, filename, fact):
        self.database().log_deleted_media(time.time(), filename, fact.id)
            
    def dump_to_txt_log(self):
        self.database().dump_to_txt_log()
        
