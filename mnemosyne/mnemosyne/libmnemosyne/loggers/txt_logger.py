#
# txt_logging <Peter.Bienstman@UGent.be>
#

import os
import sys
import logging

import mnemosyne.version
from mnemosyne.libmnemosyne.logger import Logger
from mnemosyne.libmnemosyne.stopwatch import stopwatch


class TxtLogger(Logger):
    
    def __init__(self, component_manager):
        Logger.__init__(self, component_manager)
        self.logger = logging.getLogger("mnemosyne")

    def start_logging(self):
        basedir = self.config().basedir
        log_name = os.path.join(basedir, "log.txt")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_name)
        formatter = logging.Formatter("%(asctime)s %(message)s",
                                  "%Y-%m-%d %H:%M:%S :")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Note: the code above could be simplified by using the code below.
        # However, in that case, the log file is empty on the very first
        # program invocation.  This is probably a Python bug.

        #self.logger.basicConfig(level=self.logger.INFO,
        #                    format="%(asctime)s %(message)s",
        #                    datefmt="%Y-%m-%d %H:%M:%S :",
        #                    filename=log_name)
                            
    def program_started(self):    
        self.logger.info("Program started : Mnemosyne " + \
                         mnemosyne.version.version\
                         + " " + os.name + " " + sys.platform)

    def scheduler_started(self):
        self.logger.info("Scheduler : " + self.scheduler().name)
        
    def new_database(self):
        self.logger.info("New database")
    
    def loaded_database(self):
        sch = self.scheduler()
        self.logger.info("Loaded database %d %d %d", \
                         sch.scheduled_count(), \
                         sch.non_memorised_count(), \
                         sch.active_count())
        
    def saved_database(self):
        sch = self.scheduler()        
        self.logger.info("Saved database %d %d %d", \
                         sch.scheduled_count(), \
                         sch.non_memorised_count(), \
                         sch.active_count())
        
    def new_card(self, card):
        grade = -1
        new_interval = -1 # We log the first rep separately anyhow
        self.logger.info("New item %s %d %d", card.id, grade,
                         new_interval)
        
    def imported_card(self, card):
        self.logger.info("Imported item %s %d %d %d %d %d",
                         card.id, card.grade, card.ret_reps,
                         card.last_rep, card.next_rep, card.interval)
    
    def deleted_card(self, card):
        self.logger.info("Deleted item %s", card.id)
        
    def revision(self, card, scheduled_interval, actual_interval, \
                 new_interval, noise=0):
        self.logger.info("R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f",
                         card.id, card.grade, card.easiness,
                         card.acq_reps, card.ret_reps, card.lapses,
                         card.acq_reps_since_lapse, card.ret_reps_since_lapse,
                         scheduled_interval, actual_interval,
                         new_interval, noise, stopwatch.time())
                    
    def uploaded(self, filename):
        self.logger.info("Uploaded %s" % filename)
    
    def uploading_failed(self):
        self.logger.info("Uploading failed")
        
    def program_stopped(self):    
        self.logger.info("Program stopped")  
