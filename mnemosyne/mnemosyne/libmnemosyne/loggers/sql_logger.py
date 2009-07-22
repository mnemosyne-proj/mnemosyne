#
# sql_logger.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time

from mnemosyne.libmnemosyne.logger import Logger


class SqlLogger(Logger):
                          
    def started_program(self):
        self.database().log_started_program()
        
    def stopped_program(self):
        self.database().log_stopped_program()
        
    def started_scheduler(self):
        self.database().log_started_scheduler()
            
    def loaded_database(self):
        self.database().log_loaded_database()
        
    def saved_database(self):
        self.database().log_saved_database()
        
    def added_tag(self, tag):
        self.database().log_added_tag(tag)
        
    def updated_tag(self, tag):
        self.database().log_updated_tag(tag)
                
    def deleted_tag(self, tag):
        self.database().log_deleted_tag(tag)
                
    def added_fact(self, fact):
        self.database().log_added_fact(fact)
        
    def updated_fact(self, fact):
        self.database().log_updated_fact(fact)
        
    def deleted_fact(self, fact):
        self.database().log_deleted_fact(fact)
                
    def added_card(self, card):
        self.database().log_added_card(card)
                
    def updated_card(self, card):
        self.database().log_updated_card(card)
        
    def deleted_card(self, card):
        self.database().log_deleted_card(card)
        
    def added_card_type(self, card_type):
        self.database().log_added_card_type(card_type)
                
    def updated_card_type(self, card_type):
        self.database().log_updated_card_type(card_type)
        
    def deleted_card_type(self, card_type):
        self.database().log_deleted_card_type(card_type)
        
    def repetition(self, card, scheduled_interval, actual_interval,
                   new_interval, noise=0):
        self.database().log_repetition(card, scheduled_interval,
            actual_interval, new_interval)

    def added_media(self, filename, fact):
        self.database().log_added_media(filename, fact)

    def deleted_media(self, filename, fact):
        self.database().log_deleted_media(filename, fact)
            
    def dump_to_txt_log(self):
        self.database().dump_to_txt_log()
        
