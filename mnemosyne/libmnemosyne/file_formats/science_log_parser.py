#
# science_log_parser.py <Peter.Bienstman@gmail.com> starting from code of
# Ryan Michael <kerinin@gmail.com> and Joonatan Kaartinen <jkaartinen@iki.fi>
#

import os
import sys
import bz2
import time

from mnemosyne.libmnemosyne.utils import traceback_string

DAY = 24 * 60 * 60 # Seconds in a day.


class ScienceLogParser(object):

    """Parse the txt logs and write the info it contains to a database
    object.

    This is complicated by several idiosyncrasies.

    First, before 2.0, dates were only stored with a resolution of a day.
    However, the timestamps of the logs make it possible to determine e.g.
    the actual interval with a resolution of a second. This however requires
    holding on to the exact time of the previous repetition of each card,
    while parsing the logs.

    A second, more thorny idiosyncrasy is the matter of the first grading of a
    card. When adding cards manually through the UI, users set an initial
    grade there. For cards that are imported, there is no such possibility.

    Throughout the history of Mnemosyne, several approaches have been taken
    to deal with this issue.

    Before 0.9.8, the inconsistency was simply ignored, and the initial
    grading of a card in the 'add cards' dialog was not counted as a grading.

    Starting with 0.9.8, Dirk Hermann recognised the inconsistency, and
    regardless of grade, the initial grading of a card in the 'add cards'
    dialog was always counted as an acquisition repetition. So, before any 'R'
    log entry of a card added through the 'add cards' dialog, 'acq_reps' was
    already 1. For cards imported, 'acq_reps' stayed zero.

    When later on Mnemosyne acquired the possibility to learn new cards in
    random order, a new card attribute 'unseen' needed to be introduced,
    keeping track of whether the card was already seen in the interactive
    review process. This hack complicated the code, and therefore, starting
    with Mnemosyne 2.0, a different approach was taken. The initial grading
    of a card in the 'add cards' dialog was only counted as an acquisition
    repetition (and explicitly logged as an 'R' event) when the grade was 2
    or higher. In other cases, the grade got set to -1 (signifying unseen),
    just as for imported cards.

    When parsing old logs, the data needs to be adjusted to fit the latest
    scheme. To clarify what needs to be done, the following table shows a
    summary of the contents of the logs after creating a new card through
    the GUI (giving it an initial grade at the same time), as well as the
    value of 'acq_reps' at that time.

                            initial grade 0,1      initial grade 2,3,4,5

    version < 0.9.8:        New item, acq_reps=0   New item, acq_reps=0

    0.9.8 <= version < 2.0  New item, acq_reps=1   New item, acq_reps=1

    2.0 <= version          New item, acq_reps=0   New item, acq_reps=0
                                                   R acq_reps=1


    So, to convert to the latest scheme, we need the following actions:


                            initial grade 0,1    initial grade 2,3,4,5

    version < 0.9.8:        None                 add R at creation
                                                 increase acq_reps

    0.9.8 <= version < 2.0  decrease acq_reps    add R at creation

    Since there is no grading on import, we don't need to do anything special
    for imported cards.

    The database object should implement the following API:

        def log_started_program(self, timestamp, program_name_version)
        def log_stopped_program(self, timestamp)
        def log_started_scheduler(self, timestamp, scheduler_name)
        def log_loaded_database(self, timestamp, scheduled_count,
        def log_saved_database(self, timestamp, scheduled_count,
        def log_added_card(self, timestamp, card_id)
        def log_deleted_card(self, timestamp, card_id)
        def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
            ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
            scheduled_interval, actual_interval, thinking_time, next_rep,
            scheduler_data)
        def set_offset_last_rep(self, card_id, offset, last_rep)
        def offset_last_rep(self, card_id)
        def update_card_after_log_import(id, creation_time, offset)

    Note that we don't go through the log() level of abstraction here, as this
    code is also used outside libmnemosyne for parsing logs in the statistics
    server.

    """

    versions_1_x_phase_1 = ["0.1", "0.9", "0.9.1", "0.9.2", "0.9.3", "0.9.4",
                            "0.9.5","0.9.6","0.9.7"]

    versions_1_x_phase_2 = ["0.9.8", "0.9.8.1", "0.9.9", "0.9.10", "1.0",
                            "1.0.1", "1.0.1.1", "1.0.2", "1.1", "1.1.1", "1.2",
                            "1.2.1", "1.2.2"]

    def __init__(self, database, ids_to_parse=None, machine_id=""):

        """Only convertings ids in 'ids_to_parse' makes it possible to reliably
        import different mem files (which all share the same log files).
        For efficiency reasons, 'ids_to_parse' is best a dictionary.

        """

        self.database = database
        self.ids_to_parse = ids_to_parse
        self.machine_id = machine_id
        self.version_number = "1.2.2" # Default guess for missing logs.

    def parse(self, filename):
        # Open file.
        if os.path.basename(filename) != "log.txt":
            before_extension = os.path.basename(filename).split(".")[0]
            if before_extension.count("_") == 1:
                self.user_id, self.log_number = before_extension.split("_")
            else:
                self.user_id, self.machine_id, self.log_number = \
                    before_extension.split("_")
            self.log_number = int(self.log_number)
        if os.path.getsize(filename) == 0:
            return
        if filename.endswith(".bz2"):
            self.logfile = bz2.BZ2File(filename)
        else:
            self.logfile = open(filename, "rb")
        # For pre-2.0 logs, we need to hang on to the previous timestamp, as
        # this will be used as the time the card was shown, in order to
        # calculate the actual interval. (The timestamps for repetitions are
        # when the card was graded, not when it was presented to the user.)
        self.timestamp = None
        self.previous_timestamp = None
        self.lower_timestamp_limit = 1121021345 # 2005-07-10 21:49:05.
        self.upper_timestamp_limit = time.time()
        for line in self.logfile:
            line = line.decode("utf-8")
            if line.strip() == "":
                continue
            try:
                self._parse_line(line)
            except:
                print("Ignoring error in file '%s' while parsing line:\n%s" %
                    (filename, line))
                print(traceback_string())
                sys.stdout.flush()

    def _parse_line(self, line):
        parts = line.rstrip().rsplit(" : ")
        self.timestamp = int(time.mktime(time.strptime(parts[0],
                                         "%Y-%m-%d %H:%M:%S")))
        if not self.lower_timestamp_limit < self.timestamp < \
               self.upper_timestamp_limit:
            raise TypeError("Ignoring impossible date %s" % parts[0])
        if parts[1].startswith("Program started"):
            # Parse version string. They typically look like:
            #   Mnemosyne 1.0-RC nt win32
            #   Mnemosyne 1.0 RC posix linux2
            #   Mnemosyne 1.1.1_debug3 posix linux2
            #   Mnemosyne 1.2.1 posix linux2
            self.version = parts[2].replace("_", "-")
            self.version_number = self.version.split()[1].split("-")[0]
            self.database.log_started_program(self.timestamp, self.version)
        elif parts[1].startswith("Scheduler"):
            scheduler_name = parts[2]
            self.database.log_started_scheduler(self.timestamp, scheduler_name)
        elif parts[1].startswith("Loaded database"):
            Loaded, database, scheduled, non_memorised, active = \
                parts[1].split(" ")
            self.database.log_loaded_database(self.timestamp,
                self.machine_id, int(scheduled), int(non_memorised),
                int(active))
        elif parts[1].startswith("New item"):
            self._parse_new_item(parts[1])
        elif parts[1].startswith("Imported item"):
            self._parse_imported_item(parts[1])
        elif parts[1].startswith("Deleted item"):
            self._parse_deleted_item(parts[1])
        elif parts[1].startswith("R "):
            self._parse_repetition(parts[1])
        elif parts[1].startswith("Saved database"):
            Saved, database, scheduled, non_memorised, active = \
                parts[1].split(" ")
            self.database.log_saved_database(self.timestamp,
                self.machine_id, int(scheduled), int(non_memorised),
                int(active))
        elif parts[1].startswith("Program stopped"):
            self.database.log_stopped_program(self.timestamp)
        self.previous_timestamp = self.timestamp

    def _parse_new_item(self, new_item_chunk):
        New, item, id, grade, new_interval = new_item_chunk.split(" ")
        if self.ids_to_parse and id not in self.ids_to_parse:
            return
        grade = int(grade)
        offset = 0
        if grade >= 2 and self.version_number in self.versions_1_x_phase_1:
            offset = 1
        elif grade < 2 and self.version_number in self.versions_1_x_phase_2:
            offset = -1
        self.database.log_added_card(self.timestamp, id)
        self.database.set_offset_last_rep(id, offset, last_rep=0)
        self.database.update_card_after_log_import(id, self.timestamp, offset)
        if grade >= 2 and self.version_number in \
           self.versions_1_x_phase_1 + self.versions_1_x_phase_2:
            self.database.log_repetition(self.timestamp, id, grade,
                easiness=2.5, acq_reps=1, ret_reps=0, lapses=0,
                acq_reps_since_lapse=1, ret_reps_since_lapse=0,
                scheduled_interval=0, actual_interval=0, thinking_time=0,
                next_rep=self.timestamp + int(new_interval),
                scheduler_data=0)

    def _parse_imported_item(self, imported_item_chunk):
        Imported, item, id, grade, ret_reps, last_rep, next_rep, interval \
            = imported_item_chunk.split(" ")
        if self.ids_to_parse and id not in self.ids_to_parse:
            return
        # Check if we've seen this card before. If so, we are restoring from a
        # backup and don't need to update the database.
        try:
            offset, last_rep = self.database.offset_last_rep(id)
        except:
            offset = 0
            last_rep = 0
            self.database.log_added_card(self.timestamp, id)
            self.database.set_offset_last_rep(id, offset, last_rep)
            self.database.update_card_after_log_import(id, self.timestamp,
                                                       offset)

    def _parse_deleted_item(self, deleted_item_chunk):
        Deleted, item, id = deleted_item_chunk.split(" ")
        if self.ids_to_parse and id not in self.ids_to_parse:
            return
        # Only log the deletion if we've seen the card before, as a safeguard
        # against corrupt logs.
        try:
            offset, last_rep = self.database.offset_last_rep(id)
            self.database.log_deleted_card(self.timestamp, id)
        except:
            pass

    def _parse_repetition(self, repetition_chunk):
        # Parse chunk.
        blocks = repetition_chunk.split(" | ")
        R, id, grade, easiness = blocks[0].split(" ")
        if self.ids_to_parse and id not in self.ids_to_parse:
            return
        grade = int(grade)
        easiness = float(easiness)
        acq_reps, ret_reps, lapses, acq_reps_since_lapse, \
            ret_reps_since_lapse = blocks[1].split(" ")
        acq_reps, ret_reps = int(acq_reps), int(ret_reps)
        lapses = int(lapses)
        acq_reps_since_lapse = int(acq_reps_since_lapse)
        ret_reps_since_lapse = int(ret_reps_since_lapse)
        scheduled_interval, actual_interval = blocks[2].split(" ")
        scheduled_interval = int(scheduled_interval)
        actual_interval = int(actual_interval)
        new_interval, noise = blocks[3].split(" ")
        new_interval = int(float(new_interval)) + int(noise)
        thinking_time = round(float(blocks[4]))
        # Deal with interval data for pre 2.0 logs.
        if self.version_number in \
          self.versions_1_x_phase_1 + self.versions_1_x_phase_2:
            try:
                # Calculate 'actual_interval' and update 'last_rep'.
                # (Note: 'last_rep' is the time the card was graded, not when
                # it was shown.)
                offset, last_rep = self.database.offset_last_rep(id)
                if last_rep:
                    actual_interval = self.previous_timestamp - last_rep
                else:
                    actual_interval = 0
                self.database.set_offset_last_rep(id, offset, self.timestamp)
            except TypeError:
                # Make sure the card exists (e.g. due to missing logs).
                offset = 0
                actual_interval = 0
                self.database.log_added_card(self.timestamp, id)
                self.database.set_offset_last_rep(id, offset, last_rep=0)
                self.database.update_card_after_log_import\
                (id, self.timestamp, offset)
            # Convert days to seconds.
            scheduled_interval *= DAY
            new_interval *= DAY
            # Take offset into account.
            acq_reps += offset
            if lapses == 0:
                acq_reps_since_lapse += offset
        # Log repetititon.
        self.database.log_repetition(self.timestamp, id, grade, easiness,
            acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            thinking_time, next_rep=self.timestamp + new_interval,
            scheduler_data=0)


