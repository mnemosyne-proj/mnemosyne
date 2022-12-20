#
# SQLite_logging.py <Peter.Bienstman@gmail.com>
#

import os
import time
import string
import datetime

from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.gui_translator import _

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

        # Takes 0.5 seconds on my big database for very little potential 
        # gain, so disabling this for faster startup.
        return

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
        logfile = open(logname, "a")
        sql_res = self.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()
        last_index = int(sql_res[0])
        index = 0
        # Loop over log entries and dump them to text file.
        for cursor in self.con.execute("""select _id, event_type, timestamp,
            object_id, grade, easiness, acq_reps, ret_reps, lapses,
            acq_reps_since_lapse, ret_reps_since_lapse, scheduled_interval,
            actual_interval, thinking_time, next_rep from log where _id>?""",
                        (last_index, )):
            index = int(cursor[0])
            event_type = cursor[1]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(cursor[2]))
            if event_type == EventTypes.STARTED_PROGRAM:
                print("%s : Program started : %s" \
                      % (timestamp, cursor[3]), file=logfile)
            elif event_type == EventTypes.STARTED_SCHEDULER:
                print("%s : Scheduler : %s" \
                      % (timestamp, cursor[3]), file=logfile)
            elif event_type == EventTypes.LOADED_DATABASE:
                print("%s : Loaded database %d %d %d" \
                      % (timestamp, cursor[6], cursor[7], cursor[8]), file=logfile)
            elif event_type == EventTypes.SAVED_DATABASE:
                print("%s : Saved database %d %d %d" \
                      % (timestamp, cursor[6], cursor[7], cursor[8]), file=logfile)
            elif event_type == EventTypes.ADDED_CARD:
                # Use dummy grade and interval, We log the first repetition
                # separately anyhow.
                print("%s : New item %s -1 -1" \
                      % (timestamp, cursor[3]), file=logfile)
            elif event_type == EventTypes.DELETED_CARD:
                print("%s : Deleted item %s" \
                      % (timestamp, cursor[3]), file=logfile)
            elif event_type == EventTypes.REPETITION:
                new_interval = int(cursor[14] - cursor[2])
                print("%s : R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f" %\
                         (timestamp, cursor[3], cursor[4], cursor[5],
                          cursor[6], cursor[7], cursor[8],cursor[9],
                          cursor[10], cursor[11], cursor[12], new_interval,
                          0, cursor[13]), file=logfile)
            elif event_type == EventTypes.STOPPED_PROGRAM:
                print("%s : Program stopped" % (timestamp, ), file=logfile)
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

    def merge_logs_from_other_database(self, filename, insertion_log_index):

        """This function will delete all logs in the database after
        'insertion_log_index' and merge all logs from 'filename'.

        """

        w = self.main_widget()
        w.set_progress_text(_("Merging logs..."))
        script = string.Template("""
            begin;
            delete from log where _id>$_id;
            end;
            vacuum;
            attach "$filename" as to_merge;
            begin;
            insert into log(event_type, timestamp, object_id, grade,
                easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
                ret_reps_since_lapse, scheduled_interval, actual_interval,
                thinking_time, next_rep, scheduler_data)
                select event_type, timestamp, object_id, grade, easiness,
                acq_reps, ret_reps, lapses, acq_reps_since_lapse,
                ret_reps_since_lapse, scheduled_interval, actual_interval,
                thinking_time, next_rep, scheduler_data from to_merge.log;
            commit;
        """).substitute(_id=insertion_log_index, filename=filename)
        self.con.executescript(script)
        w.close_progress()

    def archive_old_logs(self):

        """This puts all the data of old reviews in a separate file, which
        is no longer backed up. All clients do this independently, and when
        doing an initial sync, all these archive files are sent across so as
        not to lose and information. This could cause duplication, however,
        so later on a algorithm needs to be written to a create a single
        archive from these multiple files, by making sure that there are
        no log lines with duplicate (timestamps, id).

        """

        self.main_widget().set_progress_text(_("Archiving old logs..."))
        self.backup()
        one_year_ago = int(time.time()) - 356 * DAY
        # Create archive dir if needed.
        archive_dir = os.path.join(self.config().data_dir, "archive")
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        # Create empty archive database.
        db_name = os.path.basename(self.database().path()).rsplit(".", 1)[0]
        archive_name = db_name + "-" + self.config().machine_id() + "-" +\
            datetime.datetime.today().strftime("%Y%m%d-%H%M%S.db")
        archive_path = os.path.join(archive_dir, archive_name)
        from mnemosyne.libmnemosyne.databases._sqlite3 import _Sqlite3
        arch_con = _Sqlite3(self.component_manager, archive_path)
        from mnemosyne.libmnemosyne.databases.SQLite import SCHEMA
        arch_con.executescript(SCHEMA.substitute(pregenerated_data=""))
        arch_con.executescript("""drop index i_log_timestamp;
                                  drop index i_log_object_id;""")
        arch_con.commit()
        arch_con.close()
        # Needed for Android.
        self.con.execute("PRAGMA temp_store_directory='%s';" % \
                         (archive_dir, ))
        # Transfer old logs.
        script = string.Template("""
            attach "$archive_path" as archive;
            begin;
            insert into archive.log(event_type, timestamp, object_id, grade,
                easiness, acq_reps, ret_reps, lapses, acq_reps_since_lapse,
                ret_reps_since_lapse, scheduled_interval, actual_interval,
                thinking_time, next_rep, scheduler_data)
                select event_type, timestamp, object_id, grade, easiness,
                acq_reps, ret_reps, lapses, acq_reps_since_lapse,
                ret_reps_since_lapse, scheduled_interval, actual_interval,
                thinking_time, next_rep, scheduler_data from log
                    where timestamp<$one_year_ago;
            commit;
            begin;
            delete from log where timestamp<$one_year_ago;
            end;
            vacuum;
        """).substitute(archive_path=archive_path, one_year_ago=one_year_ago)
        self.con.executescript(script)
        self.main_widget().close_progress()

    def log_warn_about_too_many_cards(self, timestamp):
        self.con.execute(
            "insert into log(event_type, timestamp) values(?,?)",
            (EventTypes.WARNED_TOO_MANY_CARDS, int(timestamp)))
