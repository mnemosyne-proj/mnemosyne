#
# logger.py <Peter.Bienstman@gmail.com>
#

import os
import time

from mnemosyne.libmnemosyne.component import Component


class Logger(Component):

    component_type = "log"

    def __init__(self, component_manager):
        self.active = False
        Component.__init__(self, component_manager)

    def activate(self):
        Component.activate(self)
        self._timestamp = None
        self.upload_thread = None
        self.archive_old_log()
        self.start_logging()
        if self.config()["upload_science_logs"]:
            from mnemosyne.libmnemosyne.log_uploader import LogUploader
            self.upload_thread = LogUploader(self.component_manager)
            self.upload_thread.start()
        self.active = True

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

    def loaded_database(self, machine_id=None, scheduled_count=None,
        non_memorised_count=None, active_count=None):
        pass

    def saved_database(self, machine_id=None, scheduled_count=None,
        non_memorised_count=None, active_count=None):
        pass

    def added_card(self, card):
        pass

    def edited_card(self, card):
        pass

    def deleted_card(self, card):
        pass

    def repetition(self, card, scheduled_interval, actual_interval,
        thinking_time):
        pass

    def added_tag(self, tag):
        pass

    def edited_tag(self, tag):
        pass

    def deleted_tag(self, tag):
        pass

    def added_media_file(self, filename):
        pass

    def edited_media_file(self, filename):
        pass

    def deleted_media_file(self, filename):
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

    def added_criterion(self, criterion):
        pass

    def edited_criterion(self, criterion):
        pass

    def deleted_criterion(self, criterion):
        pass

    def edited_setting(self, key):
        pass

    def dump_to_science_log(self):
        pass

    def log_index_of_last_upload(self):

        """We don't store this info in the configuration, but determine it on
        the fly, so that users can copy configuration files between their
        machines.

        1.x log names have the format userid_index.bz2.
        2.x log names have the format userid_machineid_index.bz2

        Obviously, we should only consider the logs from our own machine.

        """

        _dir = os.listdir(os.path.join(self.config().data_dir, "history"))
        history_files = [x for x in _dir if x[-4:] == ".bz2"]
        max_log_index = 0
        this_machine_id = self.config().machine_id()
        for history_file in history_files:
            user_and_machine, log_index_and_suffix = history_file.rsplit("_", 1)
            if "_" in user_and_machine:
                user, machine = user_and_machine.split("_")
                if machine != this_machine_id:
                    continue
            log_index = int(log_index_and_suffix.split(".")[0])
            if log_index > max_log_index:
                max_log_index = log_index
        return max_log_index

    def archive_old_log(self):

        """Archive log to history folder if it's large enough."""

        if not self.config()["upload_science_logs"]:
            return
        data_dir = self.config().data_dir
        log_name = os.path.join(data_dir, "log.txt")
        try:
            log_size = os.stat(log_name).st_size
        except:
            log_size = 0
        if log_size > self.config()["max_log_size_before_upload"]:
            user = self.config()["user_id"]
            machine = self.config().machine_id()
            index = self.log_index_of_last_upload() + 1
            archive_name = "%s_%s_%05d.bz2" % (user, machine, index)
            import bz2  # Not all platforms have bz.
            f = bz2.open(os.path.join(data_dir, "history",
                archive_name), "w")
            for l in open(log_name):
                f.write(l.encode("utf-8"))
            f.close()
            os.remove(log_name)

    def deactivate(self):
        if self.upload_thread:
            from mnemosyne.libmnemosyne.gui_translator import _
            print((_("Waiting for uploader thread to stop...").encode("utf-8")))
            self.upload_thread.join()
            print((_("Done!").encode("utf-8")))

    def warn_too_many_cards(self):
        pass
