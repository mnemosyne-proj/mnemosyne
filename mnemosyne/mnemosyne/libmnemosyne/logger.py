#
# logger.py <Peter.Bienstman@UGent.be>
#

import os
import bz2

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import config


class Logger(Component):
    
    def start_logging(self):
        raise NotImplementedError
        
    def program_started(self):
        raise NotImplementedError  
        
    def new_database(self):
        raise NotImplementedError
    
    def loaded_database(self):
        raise NotImplementedError
        
    def saved_database(self):
        raise NotImplementedError
        
    def new_card(self, card):
        raise NotImplementedError  
    
    # TODO: do we need imported_fact as well?    
    def imported_card(self, card):
        raise NotImplementedError
    
    def deleted_card(self, card):
        raise NotImplementedError
        
    def revision(self, card, scheduled_interval, actual_interval, \
                 new_interval, noise):
        raise NotImplementedError               
        
    def uploaded(self, filename):
        raise NotImplementedError
    
    def uploading_failed(self):
        raise NotImplementedError
        
    def program_stopped(self):
        raise NotImplementedError      
        
    def archive_old_log(self):
        
        """Archive log to history folder if it's large enough."""
        
        basedir = config().basedir
        log_name = os.path.join(basedir, "log.txt")
        try:
            log_size = os.stat(log_name).st_size
        except:
            log_size = 0
        if log_size > 64000:
            user  = config()["user_id"]
            index = config()["log_index"]
            archive_name = "%s_%05d.bz2" % (user, index)
            f = bz2.BZ2File(os.path.join(basedir, "history", archive_name), 'w')
            for l in file(log_name):
                f.write(l)
            f.close()
            os.remove(log_name)
            config()["log_index"] = index + 1
