#
# SQLite_logging.py <Peter.Bienstman@UGent.be>
#

import os
import time

from openSM2sync.log_entry import EventTypes

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


class SQLiteLogging(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    The interface here is a bit low level, as it needs to serve both for
    logging when the program is running and for manipulating the log when
    doing a sync or importing pre-2.0 logs. (A higher level interface for the
    former use case is in logging.database_logger.)

    """

    def log_started_program(self, timestamp, version_string):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.STARTED_PROGRAM, int(timestamp), version_string))

    def log_stopped_program(self, timestamp):
        self.con.execute(\
            "insert into log(event_type, timestamp) values(?,?)",
            (EventTypes.STOPPED_PROGRAM, int(timestamp)))

    def log_started_scheduler(self, timestamp, scheduler_name):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.STARTED_SCHEDULER, int(timestamp), scheduler_name))

    def log_loaded_database(self, timestamp, machine_id, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event_type, timestamp, object_id, acq_reps,
            ret_reps, lapses) values(?,?,?,?,?,?)""",
            (EventTypes.LOADED_DATABASE, int(timestamp), machine_id,
            scheduled_count, non_memorised_count, active_count))

    def log_saved_database(self, timestamp, machine_id, scheduled_count,
        non_memorised_count, active_count):
        self.con.execute(\
            """insert into log(event_type, timestamp, object_id, acq_reps,
            ret_reps, lapses) values(?,?,?,?,?,?)""",
            (EventTypes.SAVED_DATABASE, int(timestamp), machine_id,
            scheduled_count, non_memorised_count, active_count))

    def log_future_schedule(self):

        """Write data to the logs to allow us to retrieve the scheduled count
        in case the user the user does not run Mnemosyne on that day.

        """

        timestamp = int(time.time())
        scheduled_count = 0
        for n in range(1, 8):
            timestamp += DAY
            scheduled_count += \
                self.scheduler().card_count_scheduled_n_days_from_now(n)
            self.con.execute("""insert into log(event_type, timestamp,
                object_id, acq_reps,ret_reps, lapses) values(?,?,?,?,?,?)""",
                (EventTypes.LOADED_DATABASE, timestamp,
                self.config().machine_id() + ".fut",
                scheduled_count, -666, -666))

    def log_added_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_CARD, int(timestamp), card_id))

    def log_edited_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_CARD, int(timestamp), card_id))

    def log_deleted_card(self, timestamp, card_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_CARD, int(timestamp), card_id))

    def log_repetition(self, timestamp, card_id, grade, easiness, acq_reps,
        ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
        scheduled_interval, actual_interval, thinking_time, next_rep,
        scheduler_data):
        self.con.execute(\
            """insert into log(event_type, timestamp, object_id, grade,
            easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            thinking_time, next_rep, scheduler_data)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (EventTypes.REPETITION, int(timestamp), card_id, grade, easiness,
            acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, scheduled_interval, actual_interval,
            int(thinking_time), next_rep, scheduler_data))

    def log_added_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_TAG, int(timestamp), tag_id))

    def log_edited_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_TAG, int(timestamp), tag_id))

    def log_deleted_tag(self, timestamp, tag_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_TAG, int(timestamp), tag_id))

    def log_added_media_file(self, timestamp, filename):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_MEDIA_FILE, int(timestamp), filename))

    def log_edited_media_file(self, timestamp, filename):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_MEDIA_FILE, int(timestamp), filename))

    def log_deleted_media_file(self, timestamp, filename):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_MEDIA_FILE, int(timestamp), filename))

    def log_added_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_FACT, int(timestamp), fact_id))

    def log_edited_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_FACT, int(timestamp), fact_id))

    def log_deleted_fact(self, timestamp, fact_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_FACT, int(timestamp), fact_id))

    def log_added_fact_view(self, timestamp, fact_view_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_FACT_VIEW, int(timestamp), fact_view_id))

    def log_edited_fact_view(self, timestamp, fact_view_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_FACT_VIEW, int(timestamp), fact_view_id))

    def log_deleted_fact_view(self, timestamp, fact_view_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_FACT_VIEW, int(timestamp), fact_view_id))

    def log_added_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_CARD_TYPE, int(timestamp), card_type_id))

    def log_edited_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_CARD_TYPE, int(timestamp), card_type_id))

    def log_deleted_card_type(self, timestamp, card_type_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_CARD_TYPE, int(timestamp), card_type_id))

    def log_added_criterion(self, timestamp, criterion_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.ADDED_CRITERION, int(timestamp), criterion_id))

    def log_edited_criterion(self, timestamp, criterion_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_CRITERION, int(timestamp), criterion_id))

    def log_deleted_criterion(self, timestamp, criterion_id):
        self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.DELETED_CRITERION, int(timestamp), criterion_id))

    def log_edited_setting(self, timestamp, key):
        index = self.con.execute(\
            "insert into log(event_type, timestamp, object_id) values(?,?,?)",
            (EventTypes.EDITED_SETTING, int(timestamp), key))

    def current_log_index(self):
        result = self.con.execute(\
            "select _id from log order by _id desc limit 1").fetchone()
        if result:
            return result[0]
        else:
            return 0

    def dump_to_science_log(self):
        if self.config()["upload_science_logs"] == False:
            return
        # Open log file and get starting index.
        logname = os.path.join(self.config().data_dir, "log.txt")
        logfile = file(logname, "a")
        sql_res = self.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()
        last_index = int(sql_res[0])
        index = 0
        # Loop over log entries and dump them to text file.
        for cursor in self.con.execute("""select _id, event_type, timestamp,
            object_id, grade, easiness, acq_reps, ret_reps, lapses,
            acq_reps_since_lapse, ret_reps_since_lapse, scheduled_interval,
            actual_interval, thinking_time, next_rep from log where _id>?""", (last_index, )):
            index = int(cursor[0])
            event_type = cursor[1]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(cursor[2]))
            if event_type == EventTypes.STARTED_PROGRAM:
                print >> logfile, "%s : Program started : %s" \
                      % (timestamp, cursor[3])
            elif event_type == EventTypes.STARTED_SCHEDULER:
                print >> logfile, "%s : Scheduler : %s" \
                      % (timestamp, cursor[3])
            elif event_type == EventTypes.LOADED_DATABASE:
                print >> logfile, "%s : Loaded database %d %d %d" \
                      % (timestamp, cursor[6], cursor[7], cursor[8])
            elif event_type == EventTypes.SAVED_DATABASE:
                print >> logfile, "%s : Saved database %d %d %d" \
                      % (timestamp, cursor[6], cursor[7], cursor[8])
            elif event_type == EventTypes.ADDED_CARD:
                # Use dummy grade and interval, We log the first repetition
                # separately anyhow.
                print >> logfile, "%s : New item %s -1 -1" \
                      % (timestamp, cursor[3])
            elif event_type == EventTypes.DELETED_CARD:
                print >> logfile, "%s : Deleted item %s" \
                      % (timestamp, cursor[3])
            elif event_type == EventTypes.REPETITION:
                new_interval = int(cursor[14] - cursor[2])
                print >> logfile, \
              "%s : R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f" %\
                         (timestamp, cursor[3], cursor[4], cursor[5],
                          cursor[6], cursor[7], cursor[8],cursor[9],
                          cursor[10], cursor[11], cursor[12], new_interval,
                          0, cursor[13])
            elif event_type == EventTypes.STOPPED_PROGRAM:
                print >> logfile, "%s : Program stopped" % (timestamp, )
        # Update partnership index.
        if index:
            self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
                (index, "log.txt"))

    def skip_science_log(self):

        """Bring forward the _last_log_id for the log.txt partnership, e.g.
        because some other machine took care of uploading these logs.

        """

        self.con.execute(\
            "update partnerships set _last_log_id=? where partner=?",
            (self.current_log_index(), "log.txt"))

    # The following functions are only used when importing pre-2.0 cards and
    # logs. They are needed to store temporary data about cards which is used
    # during the parsing process.

    def before_1x_log_import(self):
        if not self.con.execute("pragma table_info(cards_data)").fetchall():
            self.con.execute("""create temp table _cards(
                id text primary key,
                offset int,
                last_rep int);""")
        # Having these indexes in place while importing takes too long.
        self.con.execute("drop index if exists i_log_timestamp;")
        self.con.execute("drop index if exists i_log_object_id;")

    def after_1x_log_import(self):
        self.con.execute("drop table _cards")
        # Restore index situation.
        self.con.execute("create index i_log_timestamp on log (timestamp);")
        self.con.execute("create index i_log_object_id on log (object_id);")

    def set_offset_last_rep(self, card_id, offset, last_rep):
        self.con.execute(\
            """insert or replace into _cards(id, offset, last_rep)
            values(?,?,?)""", (card_id, offset, int(last_rep)))

    def offset_last_rep(self, card_id):
        sql_res = self.con.execute("""select offset, last_rep
           from _cards where _cards.id=?""", (card_id, )).fetchone()
        return sql_res[0], sql_res[1]

    def change_card_id(self, card, new_id):
        self.con.execute("update cards set id=? where _id=?",
            (new_id, card._id))

    def update_card_after_log_import(self, id, creation_time, offset):
        sql_res = self.con.execute("""select _id, acq_reps, lapses,
            acq_reps_since_lapse from cards where id=?""",
            (id, )).fetchone()
        acq_reps = sql_res[1] + offset
        acq_reps_since_lapse = sql_res[3]
        if sql_res[2] == 0:
            acq_reps_since_lapse += offset
        self.con.execute("""update cards set creation_time=?,
            modification_time=?, acq_reps=?, acq_reps_since_lapse=?
            where _id=?""", (creation_time, creation_time, acq_reps,
            acq_reps_since_lapse, sql_res[0]))

    def remove_card_log_entries_since(self, index):
        # Note that it is only safe to use this in case theses entries have
        # never been exposed to a sync. Their use during the import procedure
        # is therefore OK.
        self.con.execute("""delete from log where _id>? and
            (event_type=? or event_type=?)""",
            (index, EventTypes.ADDED_CARD, EventTypes.EDITED_CARD))

    def add_missing_added_card_log_entries(self, id_set):

        """Make sure all ids in 'id_set' have a card creation log entry."""

        for id in id_set - set(cursor[0] for cursor in self.con.execute(\
          "select distinct object_id from log where event_type=?",
          (EventTypes.ADDED_CARD, ))):
            self.log_added_card(int(time.time()), id)
