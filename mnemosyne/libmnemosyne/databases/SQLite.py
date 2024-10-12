#
# SQLite.py - Ed Bartosh <bartosh@gmail.com>, <Peter.Bienstman@gmail.com>
#

import os
import sys
import time
import string
import datetime
import copy as objcopy

from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.utils import traceback_string, copy
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.utils import numeric_string_cmp_key, mangle

# All ids beginning with an underscore refer to primary keys in the SQL
# database. All other id's correspond to the id's used in libmnemosyne.
# For large tables, we don't use libmnemosyne id's as primary keys for
# speed reasons (100 times slowdown in joins). We add indexes on id's
# as well, since the is the only handle we have during the sync process.

# All times are Posix timestamps.

SCHEMA = string.Template("""
    create table facts(
        _id integer primary key,
        id text,
        extra_data text default ""
    );

    /* indexes on id's are necessary for the sync protocol, which
    needs to work with id's instead of _id's. */

    create index i_facts on facts (id);

    create table data_for_fact(
        _fact_id integer,
        key text,
        value text
    );

    create index i_data_for_fact on data_for_fact (_fact_id);

    create table cards(
        _id integer primary key,
        id text,
        card_type_id text,
        _fact_id integer,
        fact_view_id text,
$pregenerated_data
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
    create index i_cards on cards (id);
    create index i_cards_2 on cards (fact_view_id); /* for card type tree */
    create index i_cards_3 on cards (_fact_id); /* for cards_from_fact */

    create table tags(
        _id integer primary key,
        id text,
        name text,
        extra_data text default ""
    );
    create index i_tags on tags (id);

    create table tags_for_card(
        _card_id integer,
        _tag_id integer
    );
    create index i_tags_for_card on tags_for_card (_card_id);
    create index i_tags_for_card_2 on tags_for_card (_tag_id);

    /* _id=1 is reserved for the currently active criterion, which could be a
    copy of another saved criterion or a completely different, unnamed
    criterion. */

    create table criteria(
       _id integer primary key,
       id text,
       name text,
       type text,
       data text
    );

    create table global_variables(
        key text,
        value text
    );

    /* Activity logs.

       For object_id, we need to store the full ids as opposed to the _ids.
       When deleting an object, there is no longer a way to get the ids from
       the _ids, and for robustness and interoperability, we need to send the
       ids across when syncing.

       We store scheduling information here, such that the contents from a log
       entry are sufficient to sync a card after a repetition. We don't need to
       store last_rep, since it's equal to timestamp.

       We also store info like scheduled_interval and actual_interval, which
       in theory could be derived from earlier log entries in the database, but
       which would be expensive staticstics to calculate. */

    create table log(
        _id integer primary key autoincrement, /* Should never be reused. */
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
        /* Storing scheduler_data allows syncing the cramming scheduler */
        scheduler_data integer
    );
    create index i_log_timestamp on log (timestamp);
    create index i_log_object_id on log (object_id);

    /* We track the last _id as opposed to the last timestamp, as importing
       another database could add log events with earlier dates, but which
       still need to be synced. Also avoids issues with clock drift. */

    create table partnerships(
        partner text unique,
        _last_log_id integer
    );

    create table media(
        filename text primary key,
        _hash text
    );

    /* Here, we store the card types that are created at run time by the user
       through the GUI, as opposed to those that are instantiated through a
       plugin. For columns containing lists, dicts, ...  like
       'fact_keys_and_names', 'unique_fact_keys', ... we store the __repr__
       representations of the Python objects.
       Since these are small tables which only get used during load to create
       card types, we only use id's instead of _ids.
       We store card_types.fact_view_ids as a repr of a list instead of as a
       separate table, because order is important. */

    create table fact_views(
        id text primary key,
        name text,
        q_fact_keys text,
        a_fact_keys text,
        q_fact_key_decorators text,
        a_fact_key_decorators text,
        a_on_top_of_q boolean default 0,
        type_answer boolean default 0,
        extra_data text default ""
    );

    create table card_types(
        id text primary key,
        name text,
        fact_keys_and_names text,
        unique_fact_keys text,
        required_fact_keys text,
        fact_view_ids text,
        keyboard_shortcuts text,
        extra_data text default ""
    );
""")

pregenerated_data = """
        question text,
        answer text,
        tags text,
"""

from mnemosyne.libmnemosyne.databases.SQLite_sync import SQLiteSync
from mnemosyne.libmnemosyne.databases.SQLite_media import SQLiteMedia
from mnemosyne.libmnemosyne.databases.SQLite_logging import SQLiteLogging
from mnemosyne.libmnemosyne.databases.SQLite_statistics import SQLiteStatistics


class SQLite(Database, SQLiteSync, SQLiteMedia, SQLiteLogging,
             SQLiteStatistics):

    """Note that most of the time, commiting is done elsewhere, e.g. by
    calling save in the main controller, in order to have a better control
    over transaction granularity.

    'store_pregenerated_data' determines whether the question, answer and tag
    strings are pregenerated and stored in the database. This is useful for
    GUIs which display the card list based directly on the SQL database. On a
    mobile device which does not need this, this can be set to 'False' to save
    resources.

    """

    version = "4"
    suffix = ".db"
    store_pregenerated_data = True

    def __init__(self, component_manager):
        Database.__init__(self, component_manager)
        self._connection = None
        self._path = None # Needed for lazy creation of connection.
        self._current_criterion = None # Cached for performance reasons.
        # Some operations have side-effects which cause additional log events,
        # like in _process_media, or when updating criteria as side effects of
        # e.g. adding tags.
        # In order to prevent duplicate log events from turning up in the sync
        # partner's log, we use the following flag to prevent these side
        # effects from generating log events while syncing.
        self.syncing = False
        # For importing from a mnemosyne2 cards file, we need different side
        # effects to be disabled/enabled.
        self.importing = False
        self.importing_with_learning_data = False

    #
    # File operations.
    #

    @property
    def con(self):

        """Connection to the database, lazily created."""

        if not self._connection:
            from mnemosyne.libmnemosyne.databases._sqlite3 import _Sqlite3
            self._connection = _Sqlite3(self.component_manager, self._path)
            #from mnemosyne.libmnemosyne.databases._apsw import _APSW
            #self._connection = _APSW(self.component_manager, self._path)
        return self._connection

    def release_connection(self):

        """Release the connection, so that it may be recreated in a separate
        thread.

        """

        if self._connection:
            self._connection.commit()
            self._connection.close()
            self._connection = None

    def path(self):
        return self._path

    def data_dir(self):
        return os.path.dirname(self._path)

    def name(self):
        return os.path.basename(self._path)

    def display_name(self):
        if not self.is_loaded():
            return None
        else:
            return os.path.basename(self._path).\
                split(self.database().suffix)[0]

    def defragment(self):
        self.main_widget().set_progress_text(_("Defragmenting database..."))
        self.con.execute("vacuum")
        # Make sure the "Untagged" tag does not show up together with
        # different tags (not sure if bug causing this has been fixed).
        untagged = self.tag("__UNTAGGED__", is_id_internal=False)
        for cursor in self.con.execute("select _id from cards"):
            _card_id = cursor[0]
            _tag_ids = [cursor2[0] for cursor2 in self.con.execute(\
                "select _tag_id from tags_for_card where _card_id=?",
                (_card_id, ))]
            if len(_tag_ids) > 1 and untagged._id in _tag_ids:
                self.con.execute(\
                    "delete from tags_for_card where _card_id=? and _tag_id=?",
                    (_card_id, untagged._id))
        # Make sure no orphaned card tags exist (not sure if bug causing
        # this has been fixed).
        self.con.execute("delete from tags_for_card where _card_id is null")
        self.main_widget().close_progress()

    def new(self, path):
        self.unload()
        self._path = expand_path(path, self.config().data_dir)
        if os.path.exists(self._path):
            os.remove(self._path)
        self.create_media_dir_if_needed()
        # Create tables.
        if self.store_pregenerated_data:
            self.con.executescript(\
                SCHEMA.substitute(pregenerated_data=pregenerated_data))
        else:
            self.con.executescript(\
                SCHEMA.substitute(pregenerated_data=""))
        self.con.execute(\
            "insert into global_variables(key, value) values(?,?)",
            ("version", self.version))
        self.con.execute("""insert into partnerships(partner, _last_log_id)
            values(?,?)""", ("log.txt", 0))
        self.config()["last_database"] = \
            contract_path(self._path, self.config().data_dir)
        # Create __UNTAGGED__ tag.
        tag = Tag("__UNTAGGED__", "__UNTAGGED__")
        self.add_tag(tag)
        # Create default criterion.
        from mnemosyne.libmnemosyne.criteria.default_criterion import \
             DefaultCriterion
        self._current_criterion = DefaultCriterion(self.component_manager)
        self._current_criterion._id = 1
        self._current_criterion.id = "__DEFAULT__"
        self._current_criterion.name = self.default_criterion_name
        self._current_criterion._tag_ids_active.add(tag._id)
        self.add_criterion(self._current_criterion)
        self.save()

    def load(self, path):
        if self.is_loaded():
            self.unload()
        self._path = expand_path(path, self.config().data_dir)
        if not os.path.exists(self._path):
            return self.new(path)
        # Check database version.
        try:
            sql_res = self.con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
        except:
            raise RuntimeError(_("Unable to load file at") + " " + self._path)
        if sql_res is None:
            raise RuntimeError(_("Unable to load file, query failed."))
        if sql_res[0] != self.version:
            if sql_res[0] == "Mnemosyne SQL 1.0":
                previous_version = 1
            else:
                previous_version = int(sql_res[0])
            try:
                if previous_version <= 2:
                    from mnemosyne.libmnemosyne.upgrades.upgrade2 \
                        import Upgrade2
                    Upgrade2(self.component_manager).run()
            except:
                raise RuntimeError(_("Database upgrade failed."))
        self.create_media_dir_if_needed()
        # Upgrade.
        self.con.execute("""create index if not exists
            i_cards_3 on cards (_fact_id);""")
        # Activate all the plugins needed for all the card types.
        # Sometimes corruption keeps the global_variables table intact,
        # but not the cards table...
        try:
            used_ids = [cursor[0] for cursor in \
                self.con.execute("select distinct card_type_id from cards")]
        except:
            raise RuntimeError(_("Unable to load file.") + traceback_string())
        # We also need to do this for the card types which are only defined
        # and have no cards yet.
        defined_in_database_ids = [cursor[0] for cursor in \
            self.con.execute("select id from card_types")]
        for id in used_ids + defined_in_database_ids:
            self.activate_plugins_for_card_type_with_id(id)
        # Instantiate card types stored in this database. Since they could
        # depend on a plugin, the card types need to be instatiated last.
        for id in defined_in_database_ids:
            card_type = self.card_type(id, is_id_internal=False)
            self.component_manager.register(card_type)
        # Finalise.
        self._current_criterion = self.criterion(1, is_id_internal=True)
        self.config()["last_database"] \
            = contract_path(path, self.config().data_dir)
        for f in self.component_manager.all("hook", "after_load"):
            f.run()
        # We don't log the database load here, but in libmnemosyne.__init__,
        # as we prefer to log the start of the program first.

    def save(self, path=None):
        # Update format.
        self.con.execute("update global_variables set value=? where key=?",
            (self.version, "version"))
        # Save database and copy it to different location if needed.
        self.con.commit()
        if not path:
            return
        dest_path = expand_path(path, self.config().data_dir)
        if dest_path != self._path:
            if sys.platform == "win32":  # pragma: no cover
                drive = os.path.splitdrive(path)[0]
                import ctypes
                if ctypes.windll.kernel32.GetDriveTypeW("%s\\" % drive) == 4:
                    raise RuntimeError(\
_("Putting a database on a network drive is forbidden under Windows to avoid data corruption."))
            copy(self._path, dest_path)
            self._path = dest_path
        self.config()["last_database"] \
            = contract_path(path, self.config().data_dir)
        # We don't log every save, as that could result in an event after
        # card repetitions.

    def backup(self):
        self.save()
        if self.config()["max_backups"] == 0:
            return
        backupdir = os.path.join(self.config().data_dir, "backups")
        db_name = os.path.basename(self._path).rsplit(".", 1)[0]
        try:
            backupfile = db_name + "-" + \
                datetime.datetime.today().strftime("%Y%m%d-%H%M%S.db")
        except:  # Work around strange Android library bug.
            from mnemosyne.libmnemosyne.utils import rand_uuid
            backupfile = db_name + "-" + rand_uuid() + ".db"
        backupfile = os.path.join(backupdir, backupfile)
        failed = False
        try:
            copy(self._path, backupfile)
        except:
            failed = True
        if failed or not os.path.exists(backupfile) or \
          not os.stat(backupfile).st_size:
            self.main_widget().show_information(\
                _("Warning: backup creation failed for") + " " +  backupfile)
            return None
        for f in self.component_manager.all("hook", "after_backup"):
            f.run(backupfile)
        # Only keep the last logs.
        files = [f for f in os.listdir(backupdir) \
                if f.startswith(db_name + "-")]
        files.sort()
        if len(files) > self.config()["max_backups"]:
            surplus = len(files) - self.config()["max_backups"]
            for file in files[0:surplus]:
                os.remove(os.path.join(backupdir, file))
        return backupfile

    def restore(self, path):
        self.abandon()
        db_path = expand_path(\
            self.config()["last_database"], self.config().data_dir)
        copy(path, db_path)
        self.load(db_path)
        # We need to indicate that a full sync needs to happen on the next
        # sync. Unfortunately, we can't do anything about the logs that have
        # already been sent to the science server, but the size of the science
        # database should mitigate that effect.
        self.reset_partnerships()

    def unload(self):
        if not self._connection:
            return
        # Unregister card types in this database.
        for cursor in self.con.execute("select id from card_types"):
            id = cursor[0]
            card_type = self.card_type(id, is_id_internal=-1)
            self.component_manager.unregister(card_type)
        # This could fail if the database got corrupted and we are trying to
        # create a new, temporary one.
        try:
            for f in self.component_manager.all("hook", "before_unload"):
                f.run()
            self.log().dump_to_science_log()
            self.backup()  # Saves too.
            self._connection.close()
        except Exception as e:
            pass
        finally:
            self._connection = None
            self._path = None
        return True

    def abandon(self):
        if self._connection:
            self._connection.close()
        self._connection = None
        self._path = None

    def is_loaded(self):
        return self._connection is not None

    def is_accessible(self):

        """Check if the database is not locked by another thread."""

        accessible = True
        try:
            sql_res = self.con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
        except:
            accessible = False
        return accessible

    def is_empty(self):
        return self.tag_count() == 1 and self.fact_count() == 0 and \
            self.con.execute("""select count() from log where event_type=? or
            event_type=? or event_type=? or event_type=?""",
            (EventTypes.ADDED_TAG, EventTypes.ADDED_FACT,
            EventTypes.ADDED_FACT_VIEW, EventTypes.ADDED_CARD_TYPE)).\
            fetchone()[0] == 0

    def _repr_extra_data(self, extra_data):
        # Use simply repr(), as pickle is overkill for a simple dictionary.
        if extra_data == {}:
            return "" # Save space.
        else:
            return repr(extra_data)

    def _construct_extra_data(self, extra_data, obj):
        if extra_data == "":
            obj.extra_data = {}
        else:
            obj.extra_data = eval(extra_data)

    #
    # Tags.
    #

    def get_or_create_tag_with_name(self, name):
        name = name.strip()
        if name.startswith("::"):
            name = name[2:]
        sql_res = self.con.execute("""select _id, id, name, extra_data from
            tags where name=?""", (name, )).fetchone()
        if sql_res:
            tag = Tag(sql_res[2], sql_res[1])
            tag._id = sql_res[0]
            self._construct_extra_data(sql_res[3], tag)
        else:
            tag = Tag(name)
            self.add_tag(tag)
        return tag

    def get_or_create_tags_with_names(self, names):
        tags = set()
        for name in names:
            name = name.strip()
            if name:
                tags.add(self.get_or_create_tag_with_name(name))
        return tags

    def add_tag(self, tag):
        tag.name = tag.name.replace(",", " - ")
        self.con.execute("""insert into tags(name, extra_data, id)
            values(?,?,?)""", (tag.name,
            self._repr_extra_data(tag.extra_data), tag.id))
        tag._id = self.con.last_insert_rowid()
        # No need to log creation of the __UNTAGGED__ tag during sync, nor the
        # adding of this tag to the default criterion. Each client will have
        # done so automatically.
        if tag.id == "__UNTAGGED__":
            return
        self.log().added_tag(tag)
        # When syncing (but not when importing), don't bother to check for
        # updates to criteria here, as there will be separate log events
        # coming later to deal with this (generated by 'update_criterion'
        # a few lines below).
        if self.syncing:
            return
        current_criterion = self.database().current_criterion()
        saved_criterion = None
        for criterion in self.criteria():
            if criterion == current_criterion and \
                criterion.id != "__DEFAULT__":
                saved_criterion = criterion
                break
        # If there is no explictly named criterion, we always activate the
        # tag except when a parent is inactive.
        if not saved_criterion:
            criteria_to_activate_tag_in = [current_criterion]
            existing_tag_for_name = {}
            for _tag in self.tags():
                existing_tag_for_name[_tag.name] = _tag
            partial_tag_name = ""
            for node in tag.name.split("::"):
                partial_tag_name += node
                if partial_tag_name != tag.name and \
                    partial_tag_name in existing_tag_for_name:
                    parent = existing_tag_for_name[partial_tag_name]
                    if not current_criterion.is_tag_active(parent):
                        criteria_to_activate_tag_in = []
                        break
                partial_tag_name += "::"
        # If there is a saved criterion active, we ask the user what to do.
        else:
            try:
                answer = self.main_widget().show_question(\
                    _("Make tag '%s' active in saved set '%s'?") % \
                    (tag.name, saved_criterion.name), _("Yes"), _("No"), "")
            except NotImplementedError:
                # We are running in a non interactive mode.
                answer = 0  # Yes
            if answer == 1:  # No.
                criteria_to_activate_tag_in = []
            else:
                criteria_to_activate_tag_in = \
                    [current_criterion, saved_criterion]
        for criterion in self.criteria():
            if criterion in criteria_to_activate_tag_in:
                criterion.active_tag_added(tag)
            else:
                criterion.deactivated_tag_added(tag)
            self.update_criterion(criterion)
        # Strictly speaking, we should reapply the default criterion here,
        # just as we do in delete_tag. However, the behaviour for new tags is
        # they are enabled by default, so we don't reapply the criterion and
        # save some time.

    def tag(self, id, is_id_internal):
        if is_id_internal:
            sql_res = self.con.execute("""select _id, id, name, extra_data
                from tags where _id=?""", (id, )).fetchone()
        else:
            sql_res = self.con.execute("""select _id, id, name, extra_data
                from tags where id=?""", (id, )).fetchone()
        tag = Tag(sql_res[2], sql_res[1])
        tag._id = sql_res[0]
        self._construct_extra_data(sql_res[3], tag)
        return tag

    def update_tag(self, tag):
        self.log().edited_tag(tag)
        # Corner case: change tag name into the name of an existing tag.
        new_name = tag.name
        stored_name = self.con.execute("select name from tags where _id=?",
            (tag._id, )).fetchone()[0]
        if new_name != stored_name and self.con.execute("""select 1 from
            tags where name=? limit 1""", (new_name, )).fetchone() is not None:
            _existing_tag_id = self.con.execute("""select _id from tags where
            name=?""", (new_name, )).fetchone()[0]
            _card_ids_affected = [cursor[0] for cursor in self.con.execute(\
                "select _card_id from tags_for_card where _tag_id=?",
                (tag._id, ))]
            for _card_id in _card_ids_affected:
                # If the card already had a tag with the updated name, delete
                # the other tag.
                if self.con.execute("""select 1 from tags_for_card where
                    _tag_id=? and _card_id=? limit 1""",
                    (_existing_tag_id, _card_id)).fetchone() is not None:
                    self.con.execute("""delete from tags_for_card where
                    _tag_id=? and _card_id=?""", (tag._id, _card_id))
                # If not, update the link.
                else:
                    self.con.execute("""update tags_for_card set _tag_id=?
                        where _tag_id=?""", (_existing_tag_id, tag._id))
                # If the operations above caused the deletion of the original
                # tag, we have not enough information in log to update the
                # cards. Therefore, generate extra EDITED_CARD events, but
                # don't duplicate these while syncing.
                if not self.syncing:
                    card_id = self.con.execute("""select id from cards where
                    _id=?""", (_card_id, )).fetchone()[0]
                    self.log_edited_card(time.time(), card_id)
            if self.store_pregenerated_data:
                self._update_tag_strings(_card_ids_affected)
            self.delete_tag_if_unused(tag)
            return
        # Regular case.
        self.con.execute("""update tags set name=?, extra_data=? where
            _id=?""", (tag.name, self._repr_extra_data(tag.extra_data),
             tag._id))
        if self.store_pregenerated_data:
            _card_ids_affected = [cursor[0] for cursor in self.con.execute(
                "select _card_id from tags_for_card where _tag_id=?",
                (tag._id, ))]
            self._update_tag_strings(_card_ids_affected)

    def _update_tag_strings(self, _card_ids):
        # To speed up the process, we don't construct the entire card object,
        # but take shortcuts.
        for _card_id in _card_ids:
            tag_names = []
            for cursor in self.con.execute("""select _tag_id from
                tags_for_card where _card_id=?""", (_card_id, )):
                tag_name = self.con.execute(\
                    "select name from tags where _id=?",
                    (cursor[0], )).fetchone()[0]
                if tag_name != "__UNTAGGED__":
                    tag_names.append(tag_name)
            sorted_tag_names = sorted(tag_names, key=numeric_string_cmp_key)
            tag_string = ", ".join(sorted_tag_names)
            self.con.execute("update cards set tags=? where _id=?",
                (tag_string, _card_id))

    def delete_tag(self, tag):
        if tag.id == "__UNTAGGED__":
            return
        self.con.execute("delete from tags where _id=?", (tag._id, ))
        _card_ids_affected = [cursor[0] for cursor in self.con.execute(
            "select _card_id from tags_for_card where _tag_id=?",
            (tag._id, ))]
        self.con.execute("delete from tags_for_card where _tag_id=?",
            (tag._id, ))
        for _card_id in _card_ids_affected:
            if self.con.execute("""select 1 from tags_for_card where
                _card_id=? limit 1""", (_card_id, )).fetchone() is None:
                untagged = self.get_or_create_tag_with_name("__UNTAGGED__")
                self.con.execute("""insert into tags_for_card(_tag_id,
                    _card_id) values(?,?)""", (untagged._id, _card_id))
        if self.store_pregenerated_data:
            self._update_tag_strings(_card_ids_affected)
        # Update criteria, as e.g. deleting a forbidden tag needs to
        # reactive the cards having this tag.
        # TODO: some speed-up could be had here be only running the applier
        # if the tag was relevant for the current criterion.
        self.log().deleted_tag(tag)
        # When syncing, don't bother to check for updates to criteria here, as
        # there will be separate log events coming later to deal with this
        # (generated by 'update_criterion' a few lines below).
        if self.syncing:
            del tag
            return
        for criterion in self.criteria():
            criterion.tag_deleted(tag)
            self.update_criterion(criterion)
        criterion = self.current_criterion()
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)
        del tag

    def delete_tag_if_unused(self, tag):
        if tag.id == "__UNTAGGED__":
            return
        if self.con.execute("""select 1 from tags as cat,
            tags_for_card as cat_c where cat_c._tag_id=cat._id and
            cat._id=? limit 1""", (tag._id, )).fetchone() is None:
            self.delete_tag(tag)

    def tags(self):

        """Return tags in a nicely sorted order, with __UNTAGGED__ at the end.

        """

        result = [self.tag(cursor[0], is_id_internal=True) for cursor in \
            self.con.execute("select _id from tags")]
        result.sort(key=lambda x: numeric_string_cmp_key(x.name))
        index = 0
        # __UNTAGGED__ is typically at the head of the list, except when tags
        # start with numbers.
        for tag in result:
            if tag.name == "__UNTAGGED__":
                untagged = result.pop(index)
                result.append(untagged)
                break
            index += 1
        return result

    def has_tag_with_id(self, id):
        return self.con.execute("select 1 from tags where id=? limit 1",
            (id, )).fetchone() is not None

    #
    # Facts.
    #

    def add_fact(self, fact):
        # Add fact to facts table.
        self.con.execute("insert into facts(id) values(?)", (fact.id, ))
        fact._id = self.con.last_insert_rowid()
        # Create data_for_fact.
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((fact._id, fact_key, value)
            for fact_key, value in fact.data.items() if value))
        self.log().added_fact(fact)
        # Process media files.
        self._process_media(fact)

    def fact(self, id, is_id_internal):
        if is_id_internal:
            sql_res = self.con.execute("""select _id, id, extra_data from
                facts where _id=?""", (id, )).fetchone()
        else:
            sql_res = self.con.execute("""select _id, id, extra_data from
                facts where id=?""", (id, )).fetchone()
        # Create dictionary with fact.data.
        fact_data = dict([(cursor[0], cursor[1]) for cursor in \
            self.con.execute("""select key, value from data_for_fact where
            _fact_id=?""", (sql_res[0], ))])
        # Create fact.
        fact = Fact(fact_data, id=sql_res[1])
        fact._id = sql_res[0]
        self._construct_extra_data(sql_res[2], fact)
        return fact

    def update_fact(self, fact):
        # Delete data_for_fact and recreate it.
        self.con.execute("delete from data_for_fact where _fact_id=?",
            (fact._id, ))
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((fact._id, key, value)
                for key, value in fact.data.items() if value))
        self.log().edited_fact(fact)
        # Process media files.
        self._process_media(fact)

    def delete_fact(self, fact):
        self.con.execute("delete from facts where _id=?", (fact._id, ))
        self.con.execute("delete from data_for_fact where _fact_id=?",
            (fact._id, ))
        self.log().deleted_fact(fact)
        del fact

    def has_fact_with_id(self, id):
        return self.con.execute("select 1 from facts where id=? limit 1",
            (id, )).fetchone() is not None

    def fact_ids_forgotten_and_learned_today(self, start_of_day, end_of_day):
        return (cursor[0] for cursor in self.con.execute(
            """
            select cards._fact_id from log inner join cards where
            log.object_id = cards.id and log.timestamp >= :start_of_day and
            log.timestamp < :end_of_day and log.event_type = :event_type and
            log.grade >= 2 and log.object_id in (
              select object_id from log where timestamp >= :start_of_day and
              timestamp < :end_of_day and event_type = :event_type and
              grade < 2 and ret_reps > 0 group by object_id)
            group by log.object_id
            """,
            {"start_of_day": start_of_day,
             "end_of_day": end_of_day,
             "event_type": EventTypes.REPETITION}).fetchall())

    def fact_ids_newly_learned_today(self, start_of_day, end_of_day):
        return (cursor[0] for cursor in self.con.execute(
            """select cards._fact_id from log inner join cards where
            log.object_id = cards.id and ?<=log.timestamp and log.timestamp<?
            and log.event_type=? and log.grade>=2 and log.ret_reps==0""",
            (start_of_day, end_of_day, EventTypes.REPETITION)).fetchall())

    #
    # Cards.
    #

    def add_card(self, card):
        # The card should at least have the __UNTAGGED__ tag. This allows for
        # an easy and fast implementation of applying criteria.
        if len(card.tags) == 0:
           card.tags.add(self.get_or_create_tag_with_name("__UNTAGGED__"))
        self.current_criterion().apply_to_card(card)
        self.con.execute("""insert into cards(id, card_type_id,
            _fact_id, fact_view_id, grade, next_rep, last_rep, easiness,
            acq_reps, ret_reps, lapses, acq_reps_since_lapse,
            ret_reps_since_lapse, creation_time, modification_time,
            extra_data, scheduler_data, active) values(?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?)""", (card.id, card.card_type.id, card.fact._id,
            card.fact_view.id, card.grade, card.next_rep, card.last_rep,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            card.creation_time, card.modification_time,
            self._repr_extra_data(card.extra_data), card.scheduler_data,
            card.active,))
        card._id = self.con.last_insert_rowid()
        if self.store_pregenerated_data:
            self.con.execute(\
                "update cards set question=?, answer=?, tags=? where _id=?",
                (card.question("plain_text"), card.answer("plain_text"),
                card.tag_string(), card._id))
        # Link card to its tags. The tags themselves have already been created
        # by default_controller calling get_or_create_tag_with_name.
        # Note: using executemany here is often slower here as cards mostly
        # have 0 or 1 tags.
        for tag in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (tag._id, card._id))
        self.log().added_card(card)

    def card(self, id, is_id_internal):
        query = """select _id, id, card_type_id, _fact_id, fact_view_id,
            grade, next_rep, last_rep, easiness, acq_reps, ret_reps, lapses,
            acq_reps_since_lapse, ret_reps_since_lapse, creation_time,
            modification_time, extra_data, scheduler_data, active from cards
            where """
        if is_id_internal:
            sql_res = self.con.execute(query + "_id=?", (id, )).fetchone()
        else:
            sql_res = self.con.execute(query + "id=?", (id, )).fetchone()
        if sql_res is None or sql_res[3] is None:
            from mnemosyne.libmnemosyne.utils import MnemosyneError
            raise MnemosyneError
        fact = self.fact(sql_res[3], is_id_internal=True)
        # Note that for the card type, we turn to the component manager as
        # opposed to this database, as we would otherwise miss the built-in
        # system card types
        card_type = self.card_type_with_id(sql_res[2])
        for fact_view in card_type.fact_views:
            if fact_view.id == sql_res[4]:
                card = Card(card_type, fact, fact_view,
                    creation_time=sql_res[14])
                break
        card._id = sql_res[0]
        card.id = sql_res[1]
        card.grade = sql_res[5]
        card.next_rep = sql_res[6]
        card.last_rep = sql_res[7]
        card.easiness = sql_res[8]
        card.acq_reps = sql_res[9]
        card.ret_reps = sql_res[10]
        card.lapses = sql_res[11]
        card.acq_reps_since_lapse = sql_res[12]
        card.ret_reps_since_lapse = sql_res[13]
        card.modification_time = sql_res[15]
        self._construct_extra_data(sql_res[16], card)
        card.scheduler_data = sql_res[17]
        card.active = sql_res[18]
        for cursor in self.con.execute("""select _tag_id from tags_for_card
            where _card_id=?""", (card._id, )):
            card.tags.add(self.tag(cursor[0], is_id_internal=True))
        return card

    def update_card(self, card, repetition_only=False):
        # The card should at least have the __UNTAGGED__ tag. This allows for
        # an easy and fast implementation of applying criteria.
        if len(card.tags) == 0:
           card.tags.add(self.get_or_create_tag_with_name("__UNTAGGED__"))
        if not repetition_only:
            self.current_criterion().apply_to_card(card)
        self.con.execute("""update cards set grade=?, next_rep=?, last_rep=?,
            easiness=?, acq_reps=?, ret_reps=?, lapses=?,
            acq_reps_since_lapse=?, ret_reps_since_lapse=?,
            scheduler_data=?, active=? where _id=?""",
            (card.grade, card.next_rep, card.last_rep, card.easiness,
            card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            card.scheduler_data, card.active, card._id))
        if repetition_only:
            return
        self.con.execute("""update cards set card_type_id=?, _fact_id=?,
            fact_view_id=?, creation_time=?, modification_time=?, extra_data=?
            where _id=?""", (card.card_type.id, card.fact._id,
            card.fact_view.id, card.creation_time, card.modification_time,
            self._repr_extra_data(card.extra_data), card._id))
        if self.store_pregenerated_data:
            self.con.execute(\
                "update cards set question=?, answer=?, tags=? where _id=?",
                (card.question("plain_text"), card.answer("plain_text"),
                card.tag_string(), card._id))
        # If repetition_only is True, there is no need to log an EDITED_CARD
        # entry here, as the REPETITION log entry will contain all the data to
        # update the card.
        self.log().edited_card(card)
        # Link card to its tags. The tags themselves have already been created
        # by default_controller calling get_or_create_tag_with_name.
        # Unused tags will also be cleaned up there.
        self.con.execute("delete from tags_for_card where _card_id=?",
                         (card._id, ))
        for tag in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (tag._id, card._id))

    def delete_card(self, card, check_for_unused_tags=True):
        if card._id is None:
            # A card which was created and deleted before a sync, so that
            # it has incomplete information.
            self.con.execute("delete from cards where id=?", (card.id, ))
        else:
            self.con.execute("delete from cards where _id=?", (card._id, ))
            self.con.execute("delete from tags_for_card where _card_id=?",
                             (card._id, ))
        if not self.syncing and check_for_unused_tags:
            for tag in card.tags:
                self.delete_tag_if_unused(tag)
        self.log().deleted_card(card)
        del card

    def tags_from_cards_with_internal_ids(self, _card_ids):
        # Since _card_ids can have many elements, we need to construct the
        # query without ? placeholders in order to prevent hitting sqlite
        # limitations.
        if len(_card_ids) == 0:
            return []
        query = \
            "select distinct _tag_id from tags_for_card where _card_id in ("
        for _card_id in _card_ids:
            query += str(_card_id) + ","
        query = query[:-1] + ")"
        return [self.tag(cursor[0], is_id_internal=True) \
                for cursor in self.con.execute(query)]

    def add_tag_to_cards_with_internal_ids(self, tag, _card_ids):
        # To make sure we don't insert the tag twice, we delete it first.
        arguments = ((tag._id, _card_id) for _card_id in _card_ids)
        self.con.executemany("""delete from tags_for_card where _tag_id=?
            and _card_id=?""", arguments)
        # Make sure we remove the __UNTAGGED__ tag.
        _tag_id_untagged = self.con.execute(\
            "select _id from tags where name='__UNTAGGED__'")\
            .fetchone()[0]
        arguments = ((_tag_id_untagged, _card_id) for _card_id in _card_ids)
        self.con.executemany("""delete from tags_for_card where _tag_id=?
            and _card_id=?""", arguments)
        # Add the new tag.
        arguments = ((tag._id, _card_id) for _card_id in _card_ids)
        self.con.executemany("""insert into tags_for_card(_tag_id, _card_id)
            values(?,?)""", arguments)
        if self.store_pregenerated_data:
            self._update_tag_strings(_card_ids)
        # Apply criterion. (There does not seem to be any watertight shortcut
        # we can take for a special case, especially when a card can have many
        # tags, so we apply the criterion in full.)
        criterion = self.current_criterion()
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)
        # We don't call 'self.log.edited_card(card)', which would require us to
        # construct the entire card object, but take a short cut.
        for _card_id in _card_ids:
            card_id = self.con.execute("select id from cards where _id=?",
                (_card_id, )).fetchone()[0]
            self.con.execute("""insert into log(event_type, timestamp,
                object_id) values(?,?,?)""",
                (EventTypes.EDITED_CARD, int(time.time()), card_id))

    def remove_tag_from_cards_with_internal_ids(self, tag, _card_ids):
        # Delete tags.
        arguments = ((tag._id, _card_id) for _card_id in _card_ids)
        self.con.executemany("""delete from tags_for_card where _tag_id=?
            and _card_id=?""", arguments)
        # Make sure we add the __UNTAGGED__ tag if needed.
        _card_ids_tagged = set([cursor[0] for cursor in
            self.con.execute ("select distinct _card_id from tags_for_card")])
        _tag_id_untagged = self.con.execute(\
            "select _id from tags where name='__UNTAGGED__'")\
            .fetchone()[0]
        arguments = ((_tag_id_untagged, _card_id) for \
            _card_id in set(_card_ids).difference(_card_ids_tagged))
        self.con.executemany("""insert into tags_for_card(_tag_id, _card_id)
            values(?,?)""", arguments)
        self.delete_tag_if_unused(tag)
        if self.store_pregenerated_data:
            self._update_tag_strings(_card_ids)
        # Apply criterion. (There does not seem to be any watertight shortcut
        # we can take for a special case, especially when a card can have many
        # tags, so we apply the criterion in full.)
        criterion = self.current_criterion()
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)
        # We don't call 'self.log.edited_card(card)', which would require us
        # to construct the entire card object, but take a short cut.
        for _card_id in _card_ids:
            card_id = self.con.execute("select id from cards where _id=?",
                (_card_id, )).fetchone()[0]
            self.con.execute("""insert into log(event_type, timestamp,
                object_id) values(?,?,?)""",
                (EventTypes.EDITED_CARD, int(time.time()), card_id))

    def has_card_with_id(self, id):
        return self.con.execute("select 1 from cards where id=? limit 1",
            (id, )).fetchone() is not None

    #
    # Fact views.
    #

    def add_fact_view(self, fact_view):
        self.con.execute("""insert into fact_views(id, name, q_fact_keys,
            a_fact_keys, q_fact_key_decorators, a_fact_key_decorators,
            a_on_top_of_q, type_answer, extra_data)
            values(?,?,?,?,?,?,?,?,?)""",
            (fact_view.id, fact_view.name, repr(fact_view.q_fact_keys),
            repr(fact_view.a_fact_keys),
            repr(fact_view.q_fact_key_decorators),
            repr(fact_view.a_fact_key_decorators), fact_view.a_on_top_of_q,
            fact_view.type_answer,
            self._repr_extra_data(fact_view.extra_data)))
        self.log().added_fact_view(fact_view)

    def fact_view(self, id, is_id_internal):
        # Since there are so few of them, we don't use internal _ids.
        # ids should be unique too.
        sql_res = self.con.execute("""select id, name, q_fact_keys,
            a_fact_keys, q_fact_key_decorators, a_fact_key_decorators,
            a_on_top_of_q, type_answer, extra_data from fact_views
            where id=?""", (id, )).fetchone()
        fact_view = FactView(sql_res[1], sql_res[0])
        fact_view.q_fact_keys = eval(sql_res[2])
        fact_view.a_fact_keys = eval(sql_res[3])
        fact_view.q_fact_key_decorators = eval(sql_res[4])
        fact_view.a_fact_key_decorators = eval(sql_res[5])
        fact_view.a_on_top_of_q = bool(sql_res[6])
        fact_view.type_answer = bool(sql_res[7])
        self._construct_extra_data(sql_res[8], fact_view)
        return fact_view

    def update_fact_view(self, fact_view):
        self.con.execute("""update fact_views set name=?, q_fact_keys=?,
            a_fact_keys=?, q_fact_key_decorators=?, a_fact_key_decorators=?,
            a_on_top_of_q=?, type_answer=?, extra_data=? where id=?""",
            (fact_view.name, repr(fact_view.q_fact_keys),
            repr(fact_view.a_fact_keys), repr(fact_view.q_fact_key_decorators),
            repr(fact_view.a_fact_key_decorators), fact_view.a_on_top_of_q,
            fact_view.type_answer,
            self._repr_extra_data(fact_view.extra_data), fact_view.id))
        self.log().edited_fact_view(fact_view)

    def delete_fact_view(self, fact_view):
        self.con.execute("delete from fact_views where id=?",
            (fact_view.id, ))
        self.log().deleted_fact_view(fact_view)
        del fact_view

    def has_fact_view_with_id(self, id):
        return self.con.execute("select 1 from fact_views where id=? limit 1",
            (id, )).fetchone() is not None

    #
    # Card types.
    #

    def activate_plugins_for_card_type_with_id(self, id):
        builtin_ids = set(card_type.id for card_type in self.card_types())
        defined_in_database_ids = [cursor[0] for cursor in \
            self.con.execute("select id from card_types")]
        # Check if parents are missing plugins.
        plugin_needed_ids = set()
        while "::" in id: # Move up one level of the hierarchy.
            id, child_name = id.rsplit("::", 1)
            if id not in builtin_ids and id not in defined_in_database_ids:
                plugin_needed_ids.add(id)
        if id not in builtin_ids and id not in defined_in_database_ids:
            plugin_needed_ids.add(id)
        for card_type_id in plugin_needed_ids:
            found = False
            for plugin in self.plugins():
                for component in plugin.components:
                    if component.component_type == "card_type" and \
                        component.id == card_type_id:
                        found = True
                        try:
                            plugin.activate()
                        except:
                            raise RuntimeError(_("Error when running plugin:") \
                                + "\n" + traceback_string())
            if not found:
                raise RuntimeError(_("Missing plugin for card type with id:") +\
                                   " " + card_type_id)

    def add_card_type(self, card_type):
        card_type.extra_data["hidden_from_UI"] = card_type.hidden_from_UI
        self.con.execute("""insert into card_types(id, name,
            fact_keys_and_names, unique_fact_keys, required_fact_keys,
            fact_view_ids, keyboard_shortcuts, extra_data)
            values (?,?,?,?,?,?,?,?)""", (card_type.id,
            card_type.name, repr(card_type.fact_keys_and_names),
            repr(card_type.unique_fact_keys),
            repr(card_type.required_fact_keys),
            repr([fact_view.id for fact_view in card_type.fact_views]),
            repr(card_type.keyboard_shortcuts),
            self._repr_extra_data(card_type.extra_data)))
        # When we are syncing/merging, make sure we correctly insert the
        # class in the inheritance hierarchy.
        card_type = self.card_type(card_type.id, is_id_internal=False)
        self.component_manager.register(card_type)
        self.log().added_card_type(card_type)
        # When syncing (but not when importing), don't bother to check for
        # updates to criteria here, as there will be separate log events
        # coming later to deal with this. (generated by 'update_criterion'
        # a few lines below).
        if self.syncing:
            return
        current_criterion = self.database().current_criterion()
        saved_criterion = None
        for criterion in self.criteria():
            if criterion == current_criterion and \
                criterion.id != "__DEFAULT__":
                saved_criterion = criterion
                break
        if not saved_criterion:
            criteria_to_activate_card_type_in = [current_criterion]
        else:
            answer = self.main_widget().show_question(\
                _("Make new card type '%s' active in saved set '%s'?") % \
                (card_type.name, saved_criterion.name), _("Yes"), _("No"), "")
            if answer == 1:  # No.
                criteria_to_activate_card_type_in = []
            else:
                criteria_to_activate_card_type_in = \
                    [current_criterion, saved_criterion]
        for criterion in self.criteria():
            if criterion in criteria_to_activate_card_type_in:
                criterion.active_card_type_added(card_type)
            else:
                criterion.deactivated_card_type_added(card_type)
            self.update_criterion(criterion)

    def card_type(self, id, is_id_internal):
        # Since there are so few of them, we don't use internal _ids.
        # ids should be unique too.
        if id in self.component_manager.card_type_with_id:
            return self.component_manager.card_type_with_id[id]
        parent_id, child_id = "", id
        if "::" in id:
            parent_id, child_id = id.rsplit("::", 1)
            parent = self.card_type(parent_id, is_id_internal=-1)
        else:
            parent = CardType(self.component_manager)
        sql_res = self.con.execute("""select name, fact_keys_and_names,
            unique_fact_keys, required_fact_keys, fact_view_ids,
            keyboard_shortcuts, extra_data from card_types where id=?""",
            (id, )).fetchone()
        card_type = type(mangle(id), (parent.__class__, ),
            {"name": sql_res[0], "id": id})(self.component_manager)
        card_type.fact_keys_and_names = eval(sql_res[1])
        card_type.unique_fact_keys = eval(sql_res[2])
        card_type.required_fact_keys = eval(sql_res[3])
        card_type.keyboard_shortcuts = eval(sql_res[5])
        self._construct_extra_data(sql_res[6], card_type)
        if "hidden_from_UI" in card_type.extra_data:
            card_type.hidden_from_UI = card_type.extra_data["hidden_from_UI"]
        card_type.fact_views = [self.fact_view(fact_view_id,
            is_id_internal=False) for fact_view_id in eval(sql_res[4])]
        return card_type

    def is_user_card_type(self, card_type):
        return self.con.execute("select 1 from card_types where id=? limit 1",
            (card_type.id, )).fetchone() is not None

    def is_in_use(self, card_type):
        return self.con.execute(\
            "select 1 from cards where card_type_id=? limit 1",
            (card_type.id, )).fetchone() is not None

    def has_clones(self, card_type):
        return self.con.execute(\
            "select 1 from card_types where id like ? limit 1",
            (card_type.id + "::%", )).fetchone() is not None

    def update_card_type(self, card_type):
        # Updating of the fact views should happen at the controller level,
        # so as not to upset the sync protocol.
        self.con.execute("""update card_types set name=?,
            fact_keys_and_names=?, unique_fact_keys=?, required_fact_keys=?,
            fact_view_ids=?, keyboard_shortcuts=?, extra_data=? where id=?""",
            (card_type.name, repr(card_type.fact_keys_and_names),
            repr(card_type.unique_fact_keys),
            repr(card_type.required_fact_keys),
            repr([fact_view.id for fact_view in card_type.fact_views]),
            repr(card_type.keyboard_shortcuts),
            self._repr_extra_data(card_type.extra_data), card_type.id))
        self.component_manager.unregister(card_type)
        self.component_manager.register(card_type)
        self.log().edited_card_type(card_type)

    def delete_card_type(self, card_type):
        # Deleting of the fact views should happen at the controller level,
        # so as not to upset the sync protocol.
        self.con.execute("delete from card_types where id=?",
            (card_type.id, ))
        self.component_manager.unregister(card_type)
        self.log().deleted_card_type(card_type)
        # When syncing, don't bother to check for updates to criteria here, as
        # there will be separate log events coming later to deal with this.
        if self.syncing:
            del card_type
            return
        for criterion in self.criteria():
            criterion.card_type_deleted(card_type)
            self.update_criterion(criterion)
        del card_type

    def has_card_type_with_id(self, id):
        #if self.con.execute("select 1 from card_types where id=? limit 1",
        #    (id, )).fetchone() is not None:
        #    return True
        #else: # It could be a built-in card type.
        return id in [card_type.id for card_type in self.card_types()]

    #
    # Criteria.
    #

    def add_criterion(self, criterion):
        self.con.execute("""insert into criteria (id, name, type, data)
            values(?,?,?,?)""", (criterion.id, criterion.name,
            criterion.criterion_type, criterion.data_to_string()))
        criterion._id = self.con.last_insert_rowid()
        # No need to log creation of the default criterion during sync. Each
        # client will have done so automatically.
        if criterion.id != "__DEFAULT__":
            self.log().added_criterion(criterion)

    def criterion(self, id, is_id_internal):
        if is_id_internal:
            sql_res = self.con.execute("""select _id, id, name, type, data
                from criteria where _id=?""", (id, )).fetchone()
        else:
            sql_res = self.con.execute("""select _id, id, name, type, data
                from criteria where id=?""", (id, )).fetchone()
        for criterion_class in \
            self.component_manager.all("criterion"):
            if criterion_class.criterion_type == sql_res[3]:
                criterion = \
                    criterion_class(self.component_manager, sql_res[1])
                criterion._id = sql_res[0]
                criterion.name = sql_res[2]
                criterion.set_data_from_string(sql_res[4])
                return criterion

    def update_criterion(self, criterion):
        self.con.execute("""update criteria set name=?, type=?, data=?
            where id=?""", (criterion.name, criterion.criterion_type,
            criterion.data_to_string(), criterion.id))
        if criterion._id == 1:
            self._current_criterion = criterion
        self.log().edited_criterion(criterion)

    def delete_criterion(self, criterion):
        self.con.execute("delete from criteria where _id=?", (criterion._id, ))
        self.log().deleted_criterion(criterion)
        del criterion

    def set_current_criterion(self, criterion):
        criterion = objcopy.copy(criterion)
        criterion._id = 1
        criterion.id = "__DEFAULT__"
        self.update_criterion(criterion)
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)

    def current_criterion(self):
        return self._current_criterion

    def criteria(self):
        return (self.criterion(cursor[0], is_id_internal=True) \
            for cursor in self.con.execute("select _id from criteria"))

    def has_criterion_with_id(self, id):
        return self.con.execute("select 1 from criteria where id=? limit 1",
            (id, )).fetchone() is not None


    #
    # Queries.
    #

    def cards_from_fact(self, fact):
        return list(self.card(cursor[0], is_id_internal=True) for cursor
            in self.con.execute("select _id from cards where _fact_id=?",
                                (fact._id, )))

    def duplicates_for_fact(self, fact, card_type):

        """Return facts with the same 'card_type.unique_fact_keys'
        data as 'fact'.

        """

        _fact_ids = set()
        for fact_key in card_type.unique_fact_keys:
            if fact._id:
                for cursor in self.con.execute("""select _fact_id from
                    data_for_fact where key=? and value=? and not
                    _fact_id=?""", (fact_key, fact[fact_key], fact._id)):
                    _fact_ids.add(cursor[0])
            else:
                # The fact has not yet been saved in the database.
                for cursor in self.con.execute("""select _fact_id from
                    data_for_fact where key=? and value=?""",
                    (fact_key, fact[fact_key])):
                    _fact_ids.add(cursor[0])
        # Now we still need to make sure these facts are from cards with
        # the correct card type.
        facts = []
        for _fact_id in _fact_ids:
            this_card_type_id = self.con.execute("""select card_type_id
                from cards where _fact_id=?""", (_fact_id, )).fetchone()[0]
            if this_card_type_id == card_type.id:
                facts.append(self.fact(_fact_id, is_id_internal=True))
        return facts

    def tag_all_duplicates(self):
        # Find the _fact_ids of the candidate duplicates, i.e. not yet taking
        # into account that duplicates in different card types are allowed and
        # that we only need to check the unique fact keys. This preprocessing
        # step speeds up the rest of the calculations.
        _fact_ids = set()
        _fact_id_for_data = {}
        for key, value, _fact_id in self.con.execute(\
            """select key, value, _fact_id from data_for_fact"""):
            if key not in _fact_id_for_data:
                _fact_id_for_data[key] = {}
            if value in _fact_id_for_data[key]:
                _fact_ids.add(_fact_id_for_data[key][value])
                _fact_ids.add(_fact_id)
            else:
                _fact_id_for_data[key][value] = _fact_id
        # Sort the candidates per card type.
        _fact_ids_in_card_type = {}
        for _fact_id in _fact_ids:
            card_type_id = self.con.execute("""select card_type_id from cards
                where _fact_id=?""", (_fact_id, )).fetchone()[0]
            if card_type_id not in _fact_ids_in_card_type:
                _fact_ids_in_card_type[card_type_id] = []
            _fact_ids_in_card_type[card_type_id].append(_fact_id)
        # Check if the duplicates are really in the fields that should be
        # unique.
        duplicate_facts = set([])
        for card_type_id in _fact_ids_in_card_type:
            facts = [self.fact(_fact_id, is_id_internal=True) for _fact_id in \
                _fact_ids_in_card_type[card_type_id]]
            for fact_key in self.card_type_with_id(card_type_id).\
                unique_fact_keys:
                for i in range(len(facts)):
                    for j in range(i + 1, len(facts)):
                        if facts[i][fact_key] == facts[j][fact_key]:
                            duplicate_facts.add(facts[i])
                            duplicate_facts.add(facts[j])
        # Tag the duplicate cards.
        _card_ids = []
        for fact in duplicate_facts:
            _card_ids += [cursor[0] for cursor in self.con.execute(\
                "select _id from cards where _fact_id=?", (fact._id, ))]
        if len(_card_ids) == 0:
            self.main_widget().show_information(_("No duplicates found."))
        else:
            self.main_widget().show_information(\
 _("Found %d duplicate cards. They have been given the tag 'DUPLICATE'.") \
            % (len(_card_ids), ))
        # We add the tags after we showed the dialog box, as adding tags can
        # trigger a dialog asking if DUPLICATE should be made active in the
        # current set.
        self.add_tag_to_cards_with_internal_ids(\
            self.get_or_create_tag_with_name(_("DUPLICATE")), _card_ids)

    def card_types_in_use(self):
        return [self.card_type_with_id(cursor[0]) for cursor in \
            self.con.execute ("select distinct card_type_id from cards")]

    def link_inverse_cards(self):

        """Identify two single-sided cards which are each other's inverse and
        convert them to use the same fact.

        """

        # Make a set of dictionaries to speed up the detection process.
        # This does not allow fool-proof detection of inverses, as in some
        # cases there could be more than one _fact_id for the same value.
        # However, it can quickly give us a set of candidates which can be
        # refined later.
        _fact_id_for_front = dict([(cursor[0], cursor[1]) \
            for cursor in self.con.execute(\
            "select value, _fact_id from data_for_fact where key='f'")])
        _fact_id_for_back = dict([(cursor[0], cursor[1]) \
            for cursor in self.con.execute(\
            "select value, _fact_id from data_for_fact where key='b'")])
        _card_id_for__fact_id = dict([(cursor[1], cursor[0]) \
            for cursor in self.con.execute(\
            "select _id, _fact_id from cards where card_type_id='1'")])
        # First do a quick and dirty detection of candidate inverses, then
        # test them in more detail to see if they fullfill all the criteria,
        # and do the conversion.
        card_type_2 = self.card_type_with_id("2")
        _fact_ids_dealt_with = []
        for key in set(_fact_id_for_front.keys()).\
            intersection(list(_fact_id_for_back.keys())):
            _fact_id_1 = _fact_id_for_front[key]
            _fact_id_2 = _fact_id_for_back[key]
            # Deal only once with a pair.
            if _fact_id_1 in _fact_ids_dealt_with or \
                _fact_id_2 in _fact_ids_dealt_with:
                continue
            # Try to keep ordering consistent.
            if _fact_id_1 > _fact_id_2:
                _fact_id_1, _fact_id_2 = _fact_id_2, _fact_id_1
            # Corner case where front and back are the same.
            if _fact_id_1 == _fact_id_2:
                continue
            # Check if they correspond to the right card type.
            if _fact_id_1 not in _card_id_for__fact_id or \
                _fact_id_2 not in _card_id_for__fact_id:
                continue
            _card_id_1 = _card_id_for__fact_id[_fact_id_1]
            _card_id_2 = _card_id_for__fact_id[_fact_id_2]
            card_1 = self.card(_card_id_1, is_id_internal=True)
            card_2 = self.card(_card_id_2, is_id_internal=True)
            # Make sure they are truly duplicates, and not coming
            # from two values for the same key in 'fact_id_for_front' and
            # 'fact_id_for_back'.
            if "b" in card_1.fact.data and "b" in card_2.fact.data and \
                (card_1.fact["f"] != card_2.fact["b"] or \
                card_1.fact["b"] != card_2.fact["f"]):
                continue
            # Tags should be equal.
            if card_1.tag_string() != card_2.tag_string():
                continue
            # Now we can do the actual conversion.
            card_1.card_type = card_type_2
            card_1.fact_view = card_type_2.fact_views[0]
            card_2.fact = card_1.fact
            card_2.card_type = card_type_2
            card_2.fact_view = card_type_2.fact_views[1]
            fact_2 = self.fact(_fact_id_2, is_id_internal=True)
            self.delete_fact(fact_2)
            self.update_card(card_1)
            self.update_card(card_2)
            # Only now is it safe to mark these cards as dealt with.
            _fact_ids_dealt_with.extend([_fact_id_1, _fact_id_2])


    #
    # Card queries used by the scheduler.
    #

    def _process_sort_key(self, sort_key):
        if sort_key == "":
            return "_id"
        elif sort_key == "random":
            return "random()"
        elif sort_key == "interval":
            return "next_rep - last_rep"
        elif sort_key == "-interval":
            return "last_rep - next_rep"
        else:
            return sort_key

    def cards(self, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards order by %s limit ?"""
            % sort_key, (limit, )))

    def active_cards(self, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 order by %s limit ?"""
            % sort_key, (limit, )))

    def cards_due_for_ret_rep(self, timestamp, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where active=1 and grade>=2
            and ?>=next_rep and ret_reps_since_lapse<=? order by %s limit ?"""
            % sort_key, (timestamp,
            self.config()["max_ret_reps_since_lapse"], limit)))

    def cards_to_relearn(self, grade, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=? and lapses>0 order by %s limit ?"""
            % sort_key, (grade, limit)))

    def cards_new_memorising(self, grade, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=? and lapses=0 order by %s limit ?"""
            % sort_key, (grade, limit)))

    def cards_unseen(self, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=-1 order by %s limit ?"""
            % sort_key, (limit, )))

    def cards_learn_ahead(self, timestamp, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade>=2 and ?<next_rep and ret_reps_since_lapse<=? 
            order by %s limit ?"""
            % sort_key, (timestamp,
            self.config()["max_ret_reps_since_lapse"], limit)))

    def recently_memorised_count(self, max_ret_reps):
        return self.con.execute("""select count() from cards where active=1
            and acq_reps>0 and ret_reps between 1 and ?""",
            (max_ret_reps, )).fetchone()[0]

    #
    # Extra queries for custom schedulers.
    #

    def set_scheduler_data(self, scheduler_data):
        self.con.execute("update cards set scheduler_data=?",
            (scheduler_data, ))

    def cards_with_scheduler_data(self, scheduler_data, sort_key="",
                                  limit=-1, max_ret_reps=-1):
        sort_key = self._process_sort_key(sort_key)
        extra_cond = "" if max_ret_reps == -1 else str(
            "and acq_reps>0 and ret_reps between 0 and " + str(max_ret_reps))
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where active=1 and scheduler_data=?
            %s order by %s limit ?"""
            % (extra_cond, sort_key), (scheduler_data, limit)))

    def scheduler_data_count(self, scheduler_data, max_ret_reps=-1):
        extra_cond = "" if max_ret_reps == -1 else str(
            "and acq_reps>0 and ret_reps between 0 and " + str(max_ret_reps))
        return self.con.execute("""select count() from cards
            where active=1 and scheduler_data=? %s """ % extra_cond,
            (scheduler_data, )).fetchone()[0]

    def has_already_warned_today(self, start_of_day, end_of_day):
        result = self.database().con.execute(
            """select timestamp from log where ? <= log.timestamp and
            log.timestamp <? and log.event_type=?""",
            (start_of_day, end_of_day,
             EventTypes.WARNED_TOO_MANY_CARDS)).fetchall()
        return True if len(result) > 0 else False

    #
    # Extra queries for language analysis.
    #

    def _where_clause_known_recognition_questions(self, card_type_ids):
        clause = "where grade>=2 and ( "
        args = []
        for card_type_id in card_type_ids:
            clause += "(card_type_id=? and fact_view_id=?) or "
            args += [card_type_id, card_type_id + ".1"]
        clause = clause.rsplit("or ", 1)[0] + ")"
        return clause, args

    def known_recognition_questions_count_from_card_types_ids(\
        self, card_type_ids):
        clause, args = \
            self._where_clause_known_recognition_questions(card_type_ids)
        return self.con.execute(\
            "select count() from cards " + clause, args).fetchone()[0]

    def known_recognition_questions_from_card_types_ids(self, card_type_ids):
        clause, args = \
            self._where_clause_known_recognition_questions(card_type_ids)
        return (cursor[0] for cursor in \
                self.con.execute("select question from cards " + clause, args))
