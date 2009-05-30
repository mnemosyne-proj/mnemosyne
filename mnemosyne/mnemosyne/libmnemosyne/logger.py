#
# logger.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.component import Component


class Logger(Component):

    component_type = "log"

    def activate(self):
        self.upload_thread = None
        self.archive_old_log()
        self.start_logging()
        self.program_started()
        if self.config()["upload_logs"] and \
               not self.config().resource_limited:
            from mnemosyne.libmnemosyne.log_uploader import LogUploader
            self.upload_thread = LogUploader(self.component_manager)
            self.upload_thread.start()
    
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
    
    def imported_card(self, card):
        raise NotImplementedError
    
    def deleted_card(self, card):
        raise NotImplementedError
        
    def revision(self, card, scheduled_interval, actual_interval, \
                 new_interval, noise=0):
        raise NotImplementedError               
        
    def uploaded(self, filename):
        raise NotImplementedError
    
    def uploading_failed(self):
        raise NotImplementedError
        
    def program_stopped(self):
        raise NotImplementedError      
        
    def archive_old_log(self):
        
        """Archive log to history folder if it's large enough."""
        
        basedir = self.config().basedir
        log_name = os.path.join(basedir, "log.txt")
        try:
            log_size = os.stat(log_name).st_size
        except:
            log_size = 0
        if log_size > 64000:
            user = self.config()["user_id"]
            index = self.config()["log_index"]
            archive_name = "%s_%05d.bz2" % (user, index)
            if not self.config().resource_limited:
                import bz2
                f = bz2.BZ2File(os.path.join(basedir, "history",
                                             archive_name), 'w')
            else:
                f = file(os.path.join(basedir, "history", archive_name), 'w')
            for l in file(log_name):
                f.write(l)
            f.close()
            os.remove(log_name)
            self.config()["log_index"] = index + 1

    def deactivate(self):
        if self.upload_thread:
            from mnemosyne.libmnemosyne.translator import _
            print _("Waiting for uploader thread to stop...")
            self.upload_thread.join()
            print _("Done!")
        self.program_stopped()
