#
# database_logger.py <Peter.Bienstman@gmail.com>
#

import os
import sys
import time
from datetime import datetime

import mnemosyne.version
from mnemosyne.libmnemosyne.logger import Logger


class DatabaseLogger(Logger):

    """Stores all the log events in the database."""

    def started_program(self, version_string=None):
        if version_string == None:
            ts = time.time()
            td = datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)
            utc_offset = int((td.microseconds + \
                (td.seconds + td.days * 24. * 3600) * 10**6) / 10**6 / 60 / 60)
            version_string = "Mnemosyne %s %s %s TZ %s" % \
                (mnemosyne.version.version, os.name, sys.platform, utc_offset)
        self.database().log_started_program(self.timestamp, version_string)

    def stopped_program(self):
        self.database().log_stopped_program(self.timestamp)

    def started_scheduler(self, scheduler_name=None):
        if scheduler_name == None:
            scheduler_name = self.scheduler().name
        self.database().log_started_scheduler(self.timestamp, scheduler_name)

    def loaded_database(self, machine_id=None, scheduled_count=None,
        non_memorised_count=None, active_count=None):
        if machine_id is None:
            machine_id = self.config().machine_id()
        if scheduled_count == None:
            scheduled_count, non_memorised_count, active_count = \
                self.review_controller().counters()
        self.database().log_loaded_database(self.timestamp, machine_id,
            scheduled_count, non_memorised_count, active_count)

    def saved_database(self, machine_id=None, scheduled_count=None,
        non_memorised_count=None, active_count=None):
        if machine_id is None:
            machine_id = self.config().machine_id()
        if scheduled_count == None:
            scheduled_count, non_memorised_count, active_count = \
                self.review_controller().counters()
        self.database().log_saved_database(self.timestamp, machine_id,
            scheduled_count, non_memorised_count, active_count)

    def future_schedule(self):
        self.database().log_future_schedule()

    def added_card(self, card):
        self.database().log_added_card(self.timestamp, card.id)

    def edited_card(self, card):
        self.database().log_edited_card(self.timestamp, card.id)

    def deleted_card(self, card):
        self.database().log_deleted_card(self.timestamp, card.id)

    def repetition(self, card, scheduled_interval, actual_interval,
                   thinking_time):
        self.database().log_repetition(self.timestamp, card.id, card.grade,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            scheduled_interval, actual_interval, thinking_time,
            card.next_rep, card.scheduler_data)

    def added_tag(self, tag):
        self.database().log_added_tag(self.timestamp, tag.id)

    def edited_tag(self, tag):
        self.database().log_edited_tag(self.timestamp, tag.id)

    def deleted_tag(self, tag):
        self.database().log_deleted_tag(self.timestamp, tag.id)

    def added_media_file(self, filename):
        self.database().log_added_media_file(self.timestamp, filename)

    def edited_media_file(self, filename):
        self.database().log_edited_media_file(self.timestamp, filename)

    def deleted_media_file(self, filename):
        self.database().log_deleted_media_file(self.timestamp, filename)

    def added_fact(self, fact):
        self.database().log_added_fact(self.timestamp, fact.id)

    def edited_fact(self, fact):
        self.database().log_edited_fact(self.timestamp, fact.id)

    def deleted_fact(self, fact):
        self.database().log_deleted_fact(self.timestamp, fact.id)

    def added_fact_view(self, fact_view):
        self.database().log_added_fact_view(self.timestamp, fact_view.id)

    def edited_fact_view(self, fact_view):
        self.database().log_edited_fact_view(self.timestamp, fact_view.id)

    def deleted_fact_view(self, fact_view):
        self.database().log_deleted_fact_view(self.timestamp, fact_view.id)

    def added_card_type(self, card_type):
        self.database().log_added_card_type(self.timestamp, card_type.id)

    def edited_card_type(self, card_type):
        self.database().log_edited_card_type(self.timestamp, card_type.id)

    def deleted_card_type(self, card_type):
        self.database().log_deleted_card_type(self.timestamp, card_type.id)

    def added_criterion(self, criterion):
        self.database().log_added_criterion(self.timestamp, criterion.id)

    def edited_criterion(self, criterion):
        self.database().log_edited_criterion(self.timestamp, criterion.id)

    def deleted_criterion(self, criterion):
        self.database().log_deleted_criterion(self.timestamp, criterion.id)

    def edited_setting(self, key):
        self.database().log_edited_setting(self.timestamp, key)

    def dump_to_science_log(self):
        self.database().dump_to_science_log()

    def warn_too_many_cards(self):
        self.database().log_warn_about_too_many_cards(self.timestamp)
