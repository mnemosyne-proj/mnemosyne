#
# txt_log_parser.py <Peter.Bienstman@UGent.be> starting from code of
# Ryan Michael <kerinin@gmail.com> and Joonatan Kaartinen <jkaartinen@iki.fi>
#

import os
import bz2
import time


class TxtLogParser(object):

    """Parse the txt logs and write the info it contains to a database
    object.

    This is complicated by several idiosyncrasies.

    First, before 2.0, dates where only stored with a resolution of a day.
    However, the timestamps of the logs make it possible to determine e.g.
    the actual interval with a resolution of a second. This however requires
    holding on to the exact time of the previous repetition of each card,
    while parsing the logs.
    
    A second, more thorny idiosyncrasy is the matter of the first grading of a
    card. When adding cards manually through the UI, there is an option to set
    an initial grade there. For cards that are imported, there is no such
    possibility.
    
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
    random order, a new card attribute 'unseen' was introduced, keeping track
    of whether the card was already seen in the interactive review process.
    This hack complicated the code, and therefore, starting with Mnemosyne
    2.0, a different approach was taken. The initial grading of a card in the
    'add cards' dialog was only counted as an acquisition repetition (and
    explicitly logged as an 'R' event) when the grade was 2 or higher. In
    other cases, the grade got set to -1 (signifying unseen), just as for
    imported cards.

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
    for imported cards. We can even ignore the import events, since the card
    will be created anyway later on during the next repetition.
                                                                 
    """

    versions_phase_1 = ["0.1", "0.9", "0.9.1", "0.9.2", "0.9.3", "0.9.4",
                        "0.9.5","0.9.6","0.9.7"]

    versions_phase_2 = ["0.9.8", "0.9.8.1", "0.9.9", "0.9.10", "1.0", "1.0.1",
                        "1.0.1.1", "1.0.2", "1.1", "1.1.1", "1.2", "1.2.1"]

    def __init__(self, filename, database):
        self.filename = filename
        self.database = database
        try:
            before_extension = filename.split(".")[0]
            self.user_id, self.log_number = \
                os.path.basename(before_extension).split('_')
            self.log_number = int(self.log_number)
            self.log_file = bz2.BZ2File(self.filename)
        except:
            raise ValueError, "%s is not a valid log file." % filename
        
    def parse(self):
        
        """For pre-2.0 logs, we need to hang on to the previous timestamp, as
        this will be used as the time the card was shown, in order to
        calculate the actual interval. (The timestamps for repetitions are
        when the card was graded, not when it was presented to the user.)

        """
        
        self.timestamp = None
        self.previous_timestamp = None
        lower_timestamp_limit = 1121021345 # 2005-07-10 21:49:05.
        upper_timestamp_limit = time.time()
        self.database.parsing_started(self.user_id, self.log_number)
        for line in self.log_file:          
            parts = line.rstrip().rsplit(" : ")           
            try:
                self.timestamp = time.mktime(time.strptime(parts[0],
                                     "%Y-%m-%d %H:%M:%S"))
            except:
                # Encountered in 48185e2d_00025.bz2.
                print "time.strptime failed on %s in line\n%s"\
                      % (filename, line)
                import traceback
                traceback.print_exc()
                self.timestamp = self.previous_timestamp
                # The line might be completely corrupted, so move on.
                continue
            if not lower_timestamp_limit < self.timestamp < \
                                                upper_timestamp_limit:
                raise TypeError, "Ignoring impossible date %s" % parts[0]
            if parts[1].startswith("Program started"):
                # Parse version string. They typically look like:
                #   Mnemosyne 1.0-RC nt win32
                #   Mnemosyne 1.0 RC posix linux2
                #   Mnemosyne 1.1.1_debug3 posix linux2
                #   Mnemosyne 1.2.1 posix linux2
                self.version = parts[2].replace("_", "-")
                self.version_number = self.version.split()[1].split("-")[0]
                self.database.log_started_program(self.timestamp, self.version)
            elif parts[1].startswith("Loaded database"):
                Loaded, database, scheduled, non_memorised, active = \
                    parts[1].split(" ")
                self.database.log_loaded_database(self.timestamp, scheduled,
                                                  non_memorised, active)
            elif parts[1].startswith("New item"):
                self._parse_new_item(parts[1])
            elif parts[1].startswith("Imported item"):
                self._parse_imported_item(parts[1])
            elif parts[1].startswith("Deleted item"):
                Deleted, item, id = parts[1].split(" ")
                self.database.log_deleted_card(self.timestamp, id)
            elif parts[1].startswith("R "):
                self._parse_repetition(parts[1])
            elif parts[1].startswith("Saved database"):
                Saved, database, scheduled, non_memorised, active = \
                    parts[1].split(" ")
                self.database.log_saved_database(self.timestamp, scheduled,
                                                 non_memorised, active)
            elif parts[1].startswith("Program stopped"):
                self.database.log_stopped_program(self.timestamp)
            self.previous_timestamp = self.timestamp
            self.database.parsing_stopped(self.user_id, self.log_number)

    def _parse_new_item(self, new_item_chunck):
        try:
            New, item, id, grade, new_interval = new_item_chunck.split(" ")
        except:
            print "Error while parsing new item:\n%s" % new_item_chunck
            return
        offset = 0
        if grade >= 2 and self.version_number in self.versions_phase_1:
            offset = 1
        elif grade < 2 and self.version_number in self.versions_phase_2:
            offset = -1
        self.database.log_added_card(self.timestamp, id)
        self.database.set_offset_last_rep_time(id, offset, last_rep_time=0)
        if grade >= 2 and self.version_number in \
           self.versions_phase_1 + self.versions_phase_2:
            self.database.log_repetition(self.timestamp, id, int(grade),
                easiness=2.5, acq_reps=1, ret_reps=0, lapses=0,
                acq_reps_since_lapse=1, ret_reps_since_lapse=0,
                scheduled_interval=0, actual_interval=0, new_interval=\
                int(new_interval), thinking_time=0)

    def _parse_imported_item(self, imported_item_chunck):
        Imported, item, id, grade, ret_reps, last_rep, next_rep, interval \
                  = imported_item_chunck.split(" ")
        self.database.log_added_card(self.timestamp, id)
        self.database.set_offset_last_rep_time(id, offset=0, last_rep_time=0)

    def _parse_repetition(self, repetition_chunck):
        # Parse chunck.
        blocks = repetition_chunck.split(" | ")
        try:
            R, id, grade, easiness = blocks[0].split(" ")
            acq_reps, ret_reps, lapses, acq_reps_since_lapse, \
                      ret_reps_since_lapse = blocks[1].split(" ")
        except:
            print "Error while parsing repetition:\n%s" % blocks[0]
            return
        scheduled_interval, actual_interval = blocks[2].split(" ")
        new_interval, noise = blocks[3].split(" ")
        thinking_time = int(float(blocks[4]))
        # Deal with offset and last_rep_time stored in database.
        try:
            offset, last_rep_time = self.database.get_offset_last_rep_time(id)
            actual_interval = self.previous_timestamp - last_rep_time
            self.database.set_offset_last_rep_time(id, offset,
                                                   self.previous_timestamp)
        except TypeError:
            # Make sure the card exists (e.g. due to missing logs).
            offset = 0
            actual_interval = 0
            self.database.set_offset_last_rep_time(id, offset=offset,
                                                   last_rep_time=0)
        # Add repetition.
        acq_reps, lapses = int(acq_reps), int(lapses)
        acq_reps_since_lapse = int(acq_reps_since_lapse)
        acq_reps += offset
        if int(lapses) == 0:
            acq_reps_since_lapse += offset
        self.database.log_repetition(self.timestamp, id, int(grade),
            float(easiness), acq_reps, int(ret_reps), lapses,
            acq_reps_since_lapse, int(ret_reps_since_lapse),
            int(scheduled_interval), int(actual_interval),
            int(new_interval) + int(noise), thinking_time)
        
