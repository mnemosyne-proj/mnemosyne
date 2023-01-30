#
# mnemosyne_format.py <Peter.Bienstman@gmail.com>
#

import os
import sqlite3
import tempfile

from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.utils import copy


class MnemosyneFormat(object):

    def __init__(self, database):
        self.database = database

    def supports(self, program_name, program_version, database_version):
        return program_name.lower() == "mnemosyne" and \
            database_version == self.database.version

    def binary_filename(self, store_pregenerated_data, interested_in_old_reps):
        self.database.release_connection()
        # Copy the database to a temporary file.
        self.tmp_name = os.path.join(os.path.dirname(self.database._path),
            "__FORSTREAMING__.db")
        copy(self.database._path, self.tmp_name)
        # Delete old reps if needed.
        if not interested_in_old_reps:
            con = sqlite3.connect(self.tmp_name)
            con.execute("delete from log where event_type=?",
                (EventTypes.REPETITION, ))
            con.commit()
            con.execute("vacuum")
            con.close()
        # Delete pregerated data if needed.
        if not store_pregenerated_data:
            con = sqlite3.connect(self.tmp_name)
            con.executescript("""
            begin;
            drop index i_cards;
            create table cards_new(
                _id integer primary key,
                id text,
                card_type_id text,
                _fact_id integer,
                fact_view_id text,
                grade integer,
                next_rep integer,
                last_rep integer,
                easiness real,
                acq_reps integer,
                ret_reps integer,
                lapses integer,
                acq_reps_since_lapse integer,
                ret_reps_since_lapse integer,
                creation_time integer,
                modification_time integer,
                extra_data text default "",
                scheduler_data integer default 0,
                active boolean default 1
            );
            insert into cards_new select _id, id, card_type_id, _fact_id,
                fact_view_id, grade, next_rep, last_rep, easiness, acq_reps,
                ret_reps, lapses, acq_reps_since_lapse, ret_reps_since_lapse,
                creation_time, modification_time, extra_data, scheduler_data,
                active from cards;
            drop table cards;
            alter table cards_new rename to cards;
            create index i_cards on cards (id);
            commit;
            vacuum;
            """)
            con.close()
        return self.tmp_name

    def clean_up(self):
        os.remove(self.tmp_name)
