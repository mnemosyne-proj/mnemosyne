#
# logger.py <Peter.Bienstman@UGent.be>
#

import os
import time

from mnemosyne.libmnemosyne.component import Component


class Logger(Component):

    component_type = "log"

    def activate(self):
        self._timestamp = None
        self.upload_thread = None
        self.archive_old_log()
        self.start_logging()
        if self.config()["upload_science_logs"]:
            from mnemosyne.libmnemosyne.log_uploader import LogUploader
            self.upload_thread = LogUploader(self.component_manager)
            self.upload_thread.start()

    def get_timestamp(self):

        """If self._timestamp == None (the default), then the timestamp will
        be the current time. It is useful to be able to override this, e.g.
        during database import or syncing, when you need to add log entries
        to the database that happened in the past.

        """
        
        if self._timestamp == None:
            return time.time()
        else:
            return self._timestamp
        
    def set_timestamp(self, timestamp):
        self._timestamp = timestamp

    timestamp = property(get_timestamp, set_timestamp)
    
    def start_logging(self):
        pass
    
    def started_program(self, version_string=None):
        pass
        
    def stopped_program(self):
        pass
    
    def started_scheduler(self, scheduler_name=None):
        pass

    def loaded_database(self, scheduled_count=None, non_memorised_count=None,
        active_count=None):
        pass
        
    def saved_database(self, scheduled_count=None, non_memorised_count=None,
        active_count=None):
        pass

    def added_card(self, card):
        pass

    def edited_card(self, card):
        pass
    
    def deleted_card(self, card):
        pass
        
    def repetition(self, card, scheduled_interval, actual_interval,
                   new_interval, thinking_time):
        pass

    def added_tag(self, tag):
        pass

    def edited_tag(self, tag):
        pass
    
    def deleted_tag(self, tag):
        pass

    def added_media(self, filename):
        pass
    
    def edited_media(self, filename):
        pass
    
    def deleted_media(self, filename):
        pass
 
    def added_fact(self, fact):
        pass

    def edited_fact(self, fact):
        pass
    
    def deleted_fact(self, fact):
        pass
    
    def added_fact_view(self, fact_view):
        pass

    def edited_fact_view(self, fact_view):
        pass
    
    def deleted_fact_view(self, fact_view):
        pass
    
    def added_card_type(self, card_type):
        pass

    def edited_card_type(self, card_type):
        pass
    
    def deleted_card_type(self, card_type):
        pass
    
    def added_activity_criterion(self, activity_criterion):
        pass

    def edited_activity_criterion(self, activity_criterion):
        pass
    
    def deleted_activity_criterion(self, activity_criterion):
        pass
    
    def dump_to_science_log(self):
        pass
        
    def archive_old_log(self):
        
        """Archive log to history folder if it's large enough."""

        if not self.config()["upload_science_logs"]:
            return
        basedir = self.config().basedir
        log_name = os.path.join(basedir, "log.txt")
        try:
            log_size = os.stat(log_name).st_size
        except:
            log_size = 0
        if log_size > 64000:
            user = self.config()["user_id"]
            machine = self.config().machine_id()
            index = self.config()["log_index"]
            archive_name = "%s_%s_%05d.bz2" % (user, machine, index)
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