#
# upgrade_beta_11.py <Peter.Bienstman@UGent.be>
#

import sqlite3

from mnemosyne.libmnemosyne.component import Component

script = """
begin transaction;

create temporary table log_backup(
        _id integer primary key autoincrement,
        event_type integer,
        timestamp integer,
        object_id text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        scheduled_interval integer,
        actual_interval integer,
        thinking_time integer,
        next_rep integer,
        scheduler_data integer
    );

insert into log_backup select
        _id,
        event_type,
        timestamp,
        object_id,
        grade,
        easiness,
        acq_reps,
        ret_reps,
        lapses,
        acq_reps_since_lapse,
        ret_reps_since_lapse,
        scheduled_interval,
        actual_interval,
        thinking_time,
        next_rep,
        scheduler_data from log;

drop table log;

create table log(
        _id integer primary key autoincrement,
        event_type integer,
        timestamp integer,
        object_id text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        scheduled_interval integer,
        actual_interval integer,
        thinking_time integer,
        next_rep integer,
        scheduler_data integer
    );

insert into log select
        _id,
        event_type,
        timestamp,
        object_id,
        grade,
        easiness,
        acq_reps,
        ret_reps,
        lapses,
        acq_reps_since_lapse,
        ret_reps_since_lapse,
        scheduled_interval,
        actual_interval,
        thinking_time,
        next_rep,
        scheduler_data from log_backup;

drop table log_backup;
commit;
vacuum;
"""

class UpgradeBeta11(Component):

    def run(self):
        try:
            self.database().con.execute(\
                "select new_interval from log where _id=1")
            upgrade_needed = True
        except sqlite3.OperationalError:
            upgrade_needed = False
        if upgrade_needed:
            self.main_widget().show_information(\
                "About to upgrade database. This might take a while...")
            self.database().con.executescript(script)