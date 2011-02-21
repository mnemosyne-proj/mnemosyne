#
# SQLite.py - Ed Bartosh <bartosh@gmail.com>, <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import time
import string
import shutil
import sqlite3
import datetime

from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from mnemosyne.libmnemosyne.utils import mangle, copy_file_to_dir
from mnemosyne.libmnemosyne.utils import expand_path, contract_path

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)

# All ids beginning with an underscore refer to primary keys in the SQL
# database. All other id's correspond to the id's used in libmnemosyne.
# We don't use libmnemosyne id's as primary keys for speed reasons
# (100 times slowdown in joins). We add indices on id's as well, since
# the is the only handle we have during the sync process.

# All times are Posix timestamps.

SCHEMA = string.Template("""
    begin;
    
    create table facts(
        _id integer primary key,
        id text,
        extra_data text default ""
    );
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

    /* For object_id, we need to store the full ids as opposed to the _ids.
       When deleting an object, there is no longer a way to get the ids from
       the _ids, and for robustness and interoperability, we need to send the
       ids across when syncing.
    */
       
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
        new_interval integer,
        thinking_time integer,
        last_rep integer,
        next_rep integer,
        scheduler_data integer
    );
    create index i_log_timestamp on log (timestamp);
    create index i_log_object_id on log (object_id);
    
    /* We track the last _id as opposed to the last timestamp, as importing
       another database could add log events with earlier dates, but which
       still need to be synced. Also avoids issues with clock drift. */
    
    create table partnerships(
        partner text,
        _last_log_id integer
    );
    
    create table media(
        filename text primary key,
        _hash text
    );
    
    /* Here, we store the card types that are created at run time by the user
       through the GUI, as opposed to those that are instantiated through a
       plugin. For columns containing lists, dicts, ...  like 'fields',
       'unique_fields', ... we store the __repr__ representations of the
       Python objects.
    */

    create table fact_views(
        _id integer primary key,
        id text,
        name text,
        q_fields text,
        a_fields text,
        a_on_top_of_q boolean default 0,
        type_answer boolean default 0,
        extra_data text default ""
    );

    create table card_types(
        id text unique,
        name text,
        fields text,
        unique_fields text,
        required_fields text,
        keyboard_shortcuts text,
        extra_data text default ""
    );

    create table fact_views_for_card_type(
        _fact_view_id integer,
        card_type_id text
    );
    
    commit;
""")

pregenerated_data = """
        question text,
        answer text,
        tags text,
"""
        
from mnemosyne.libmnemosyne.databases.SQLite_sync import SQLiteSync
from mnemosyne.libmnemosyne.databases.SQLite_logging import SQLiteLogging
from mnemosyne.libmnemosyne.databases.SQLite_statistics import SQLiteStatistics

class SQLite(Database, SQLiteSync, SQLiteLogging, SQLiteStatistics):

    """Note that most of the time, Commiting is done elsewhere, e.g. by
    calling save in the main controller, in order to have a better control
    over transaction granularity.

    'store_pregenerated_data' determines whether the question, answer and tag
    strings are pregenerated and stored in the database. This is useful for
    GUIs which display the card list based directly on the SQL database. On a
    mobile device which does not need this, this can be set to 'False' to save
    resources.

    """

    version = "Mnemosyne SQL 1.0"
    suffix = ".db"
    store_pregenerated_data = True

    def __init__(self, component_manager):
        Database.__init__(self, component_manager)
        self._connection = None
        self._path = None # Needed for lazy creation of connection.
        self._current_criterion = None # Cached for performance reasons.
        self.syncing = False # Controls whether _process_media should log.

    #
    # File operations.
    #
    
    @property
    def con(self):
        
        """Connection to the database, lazily created."""

        if not self._connection:
            self._connection = sqlite3.connect(self._path, timeout=0.1,
                               isolation_level="EXCLUSIVE")
            self._connection.row_factory = sqlite3.Row
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
    
    def name(self):
        return os.path.basename(self.config()["path"])
        
    def display_name(self):
        if not self.is_loaded():
            return None
        else:
            return os.path.basename(self.config()["path"]).\
                   split(self.database().suffix)[0]
        
    def media_dir(self):
        return os.path.join(self.config().data_dir,
            os.path.basename(self.config()["path"]) + "_media")
    
    def new(self, path):
        self.unload()
        self._path = expand_path(path, self.config().data_dir)
        if os.path.exists(self._path):
            os.remove(self._path)
        # Create tables.
        if self.store_pregenerated_data:
            self.con.executescript(\
                SCHEMA.substitute(pregenerated_data=pregenerated_data))
        else:
            self.con.executescript(\
                SCHEMA.substitute(pregenerated_data=""))            
        self.con.execute("insert into global_variables(key, value) values(?,?)",
            ("version", self.version))
        self.con.execute("""insert into partnerships(partner, _last_log_id)
            values(?,?)""", ("log.txt", 0))
        self.config()["path"] = contract_path(self._path, self.config().data_dir)
        # Create default criterion.
        from mnemosyne.libmnemosyne.criteria.default_criterion import \
             DefaultCriterion
        self._current_criterion = DefaultCriterion(self.component_manager)
        self.add_criterion(self._current_criterion)
        # Create media directory.
        media_dir = self.media_dir()
        if not os.path.exists(media_dir):
            os.mkdir(media_dir)
            os.mkdir(os.path.join(media_dir, "_latex"))

    def _activate_plugin_for_card_type(self, card_type_id):
        found = False
        for plugin in self.plugins():
            for component in plugin.components:
                if component.component_type == "card_type" and \
                    component.id == card_type_id:
                    found = True
                    try:
                        plugin.activate()
                    except:
                        raise RuntimeError, _("Error when running plugin:") \
                            + "\n" + traceback_string()
        if not found:
            raise RuntimeError, _("Missing plugin for card type with id:") \
                + " " + card_type_id

    def load(self, path):
        if self.is_loaded():
            self.unload()
        self._path = expand_path(path, self.config().data_dir)
        # Check database version.
        try:
            sql_res = self.con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
        except sqlite3.OperationalError:
            self.main_widget().show_error(
                _("Another copy of Mnemosyne is still running.") + "\n" + \
                _("Continuing is impossible and will lead to data loss!"))
            sys.exit()
        except:
            raise RuntimeError, _("Unable to load file.") + traceback_string()    
        if sql_res["value"] != self.version:
            raise RuntimeError, \
                _("Unable to load file: database version mismatch.")
        # Instantiate card types stored in this database.
        for cursor in self.con.execute("select id from card_types"):
            id = cursor[0]
            card_type = self.card_type(id, id_is_internal=-1)
            self.component_manager.register(card_type)
        # Identify missing plugins for card types and their parents.
        plugin_needed = set()
        active_ids = set(card_type.id for card_type in self.card_types())
        for cursor in self.con.execute("""select distinct card_type_id
            from cards"""):
            id = cursor[0]
            while "::" in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit("::", 1)
                if id not in active_ids:
                    plugin_needed.add(id)
            if id not in active_ids:
                plugin_needed.add(id)
        for card_type_id in plugin_needed:
            try:
                self._activate_plugin_for_card_type(card_type_id)
            except RuntimeError, exception:
                self._connection.close()
                self._connection = None
                raise exception
        self._current_criterion = self.criterion(1, id_is_internal=True)
        self.config()["path"] = contract_path(path, self.config().data_dir)
        for f in self.component_manager.all("hook", "after_load"):
            f.run()
        # We don't log the database load here, as we prefer to log the start
        # of the program first.
        
    def save(self, path=None):
        # Update format.
        self.con.execute("update global_variables set value=? where key=?",
                         (self.version, "version" ))
        # Save database and copy it to different location if needed.
        self.con.commit()
        if not path:
            return
        dest_path = expand_path(path, self.config().data_dir)
        if dest_path != self._path:
            shutil.copy(self._path, dest_path)
            self._path = dest_path
        self.config()["path"] = contract_path(path, self.config().data_dir)
        # We don't log every save, as that would result in an event after
        # card repetitions.

    def backup(self):
        self.save()
        if self.config()["backups_to_keep"] == 0:
            return
        backupdir = os.path.join(self.config().data_dir, "backups")
        db_name = os.path.basename(self._path).rsplit(".", 1)[0]
        backupfile = db_name + "-" + \
            datetime.datetime.today().strftime("%Y%m%d-%H%M%S.db")
        backupfile = os.path.join(backupdir, backupfile)
        failed = False
        try:
            shutil.copy(self._path, backupfile)
        except:
            failed = True
        if failed or not os.path.exists(backupfile) or \
          not os.stat(backupfile).st_size:
            self.main_widget().show_information(\
                _("Warning: backup creation failed for") + " " +  backupfile)
        for f in self.component_manager.all("hook", "after_backup"):
            f.run(backupfile)
        # Only keep the last logs.
        if self.config()["backups_to_keep"] < 0:
            return backupfile
        files = [f for f in os.listdir(unicode(backupdir)) \
                if f.startswith(db_name + "-")]
        files.sort()
        if len(files) > self.config()["backups_to_keep"]:
            surplus = len(files) - self.config()["backups_to_keep"]
            for file in files[0:surplus]:
                os.remove(os.path.join(backupdir, file))
        return backupfile

    def restore(self, path):
        self.abandon()
        db_path = expand_path(self.config()["path"], self.config().data_dir)
        shutil.copy(path, db_path)
        self.load(db_path)

    def unload(self):
        if not self._connection:
            return
        # This could fail if the database got corrupted and we are trying to
        # create a new, temporary one.
        try:
            for f in self.component_manager.all("hook", "before_unload"):
                f.run()
            self.log().dump_to_science_log()
            self.backup()  # Saves too.         
            self._connection.close()
        except:
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

    def is_empty(self):
        return self.tag_count() == 0 and self.fact_count() == 0 and \
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

    def _get_extra_data(self, sql_res, obj):
        if sql_res["extra_data"] == "":
            obj.extra_data = {}
        else:
            obj.extra_data = eval(sql_res["extra_data"])

    #
    # Tags.
    #

    def get_or_create_tag_with_name(self, name):
        name = name.strip()
        sql_res = self.con.execute("select * from tags where name=?",
            (name, )).fetchone()
        if sql_res:
            tag = Tag(sql_res["name"], sql_res["id"])
            tag._id = sql_res["_id"]
            self._get_extra_data(sql_res, tag)
        else:
            tag = Tag(name)
            self.add_tag(tag)
        return tag

    def get_or_create_tags_with_names(self, names):
        # If there are no tags, use an artificial __UNTAGGED__ tag. This
        # allows for an easy and fast implementation of applying criteria.
        tags = set()
        for name in names:
            name = name.strip()
            if name and name != "__UNTAGGED__":
                tags.add(self.get_or_create_tag_with_name(name))
        if len(tags) == 0:
            tags.add(self.get_or_create_tag_with_name("__UNTAGGED__"))
        return tags
    
    def add_tag(self, tag):
        _id = self.con.execute("""insert into tags(name, extra_data, id)
            values(?,?,?)""", (tag.name,
            self._repr_extra_data(tag.extra_data), tag.id)).lastrowid
        tag._id = _id
        self.log().added_tag(tag)
        for criterion in self.criteria():
            criterion.tag_created(tag)
            self.update_criterion(criterion)

    def tag(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from tags where _id=?",
                                       (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from tags where id=?",
                                       (id, )).fetchone()            
        tag = Tag(sql_res["name"], sql_res["id"])
        tag._id = sql_res["_id"]
        self._get_extra_data(sql_res, tag)
        return tag

    def update_tag(self, tag):
        self.log().edited_tag(tag)
        # Corner case: change tag name into the name of an existing tag.
        new_name = tag.name
        stored_name = self.con.execute("select name from tags where _id=?",
            (tag._id, )).fetchone()[0]
        if new_name != stored_name and self.con.execute("""select count() from
            tags where name=?""", (new_name, )).fetchone()[0] != 0:
            _existing_tag_id = self.con.execute("""select _id from tags where
            name=?""", (new_name, )).fetchone()[0]
            if self.store_pregenerated_data:
                affected_card__ids = [cursor[0] for cursor in \
                    self.con.execute(
                    "select _card_id from tags_for_card where _tag_id=?",
                    (tag._id, ))]
            self.con.execute("""update tags_for_card set _tag_id=? where
                _tag_id=?""", (_existing_tag_id, tag._id))
            if self.store_pregenerated_data:
                self._update_tag_strings(affected_card__ids)
            self.remove_tag_if_unused(tag)
            return
        # Regular case.
        self.con.execute("""update tags set name=?, extra_data=? where
            _id=?""", (tag.name, self._repr_extra_data(tag.extra_data),
             tag._id))
        if self.store_pregenerated_data:
            affected_card__ids = [cursor[0] for cursor in self.con.execute(
                "select _card_id from tags_for_card where _tag_id=?",
                (tag._id, ))]
            self._update_tag_strings(affected_card__ids)

    def _update_tag_strings(self, card__ids):
        # To speed up the process, we don't construct the entire card object,
        # but take shortcuts.
        for _card_id in card__ids:
            tag_names = []
            for cursor in self.con.execute("""select _tag_id from
                tags_for_card where _card_id=?""", (_card_id, )):
                tag_name = self.con.execute(\
                    "select name from tags where _id=?",
                    (cursor["_tag_id"], )).fetchone()[0]
                if tag_name != "__UNTAGGED__":
                    tag_names.append(tag_name)
            sorted_tag_names = sorted(tag_names, cmp=numeric_string_cmp)
            tag_string = ", ".join(sorted_tag_names)
            self.con.execute("update cards set tags=? where _id=?",
                (tag_string, _card_id))            
    
    def delete_tag(self, tag):
        self.con.execute("delete from tags where _id=?", (tag._id, ))
        affected_card__ids = [cursor[0] for cursor in self.con.execute(
            "select _card_id from tags_for_card where _tag_id=?",
            (tag._id, ))]
        self.con.execute("delete from tags_for_card where _tag_id=?",
            (tag._id, ))
        for _card_id in affected_card__ids:
            if self.con.execute("""select count() from tags_for_card where
                _card_id=?""", (_card_id, )).fetchone()[0] == 0:
                untagged = self.get_or_create_tag_with_name("__UNTAGGED__")
                self.con.execute("""insert into tags_for_card(_tag_id,
                    _card_id) values(?,?)""", (untagged._id, _card_id))
        if self.store_pregenerated_data:
            self._update_tag_strings(affected_card__ids)
        # Update criteria, as e.g. deleting a forbidden tag needs to
        # reactive the cards having this tag.
        # TODO: some speed-up could be had here be only running the applier
        # if the tag was relevant for the current criterion.
        self.log().deleted_tag(tag)
        for criterion in self.criteria():
            criterion.tag_deleted(tag)
            self.update_criterion(criterion)
        criterion = self.current_criterion()
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)
        del tag
        
    def remove_tag_if_unused(self, tag):
        if self.con.execute("""select count() from tags as cat,
            tags_for_card as cat_c where cat_c._tag_id=cat._id and
            cat._id=?""", (tag._id, )).fetchone()[0] == 0:
            self.delete_tag(tag)
            
    def tags(self):

        """Return tags in a nicely sorted order, with __UNTAGGED__ at the end.

        """
        
        result = [self.tag(cursor[0], id_is_internal=True) for cursor in \
            self.con.execute("select _id from tags")]
        result.sort(key=lambda x: x.name, cmp=numeric_string_cmp)
        if result and result[0].name == "__UNTAGGED__":
            untagged = result.pop(0)
            result.append(untagged)
        return result

    #
    # Facts.
    #
    
    def add_fact(self, fact):
        # Add fact to facts table.
        _fact_id = self.con.execute("insert into facts(id) values(?)",
            (fact.id, )).lastrowid
        fact._id = _fact_id
        # Create data_for_fact.        
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((_fact_id, key, value)
            for key, value in fact.data.items()))
        self.log().added_fact(fact)
        # Process media files.
        self._process_media(fact)

    def fact(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from facts where _id=?",
                                       (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from facts where id=?",
                                       (id, )).fetchone()            
        # Create dictionary with fact.data.
        data = dict([(cursor["key"], cursor["value"]) for cursor in
            self.con.execute("select * from data_for_fact where _fact_id=?",
            (sql_res["_id"], ))])            
        # Create fact. Note that for the card type, we turn to the component
        # manager as opposed to this database, as we would otherwise miss the
        # built-in system card types.
        fact = Fact(data, id=sql_res["id"])
        fact._id = sql_res["_id"]
        self._get_extra_data(sql_res, fact)
        return fact
    
    def update_fact(self, fact):
        # Delete data_for_fact and recreate it.
        self.con.execute("delete from data_for_fact where _fact_id=?",
            (fact._id, ))
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((fact._id, key, value)
                for key, value in fact.data.items()))
        self.log().edited_fact(fact)
        # Process media files.
        self._process_media(fact)

    def delete_fact_and_sister_cards(self, fact):
        for card in self.cards_from_fact(fact):
            self.delete_card(card)
        self.con.execute("delete from facts where _id=?", (fact._id, ))
        self.con.execute("delete from data_for_fact where _fact_id=?",
            (fact._id, ))
        self.log().deleted_fact(fact)
        del fact

    #
    # Cards.
    #
    
    def add_card(self, card):
        self.current_criterion().apply_to_card(card)
        _card_id = self.con.execute("""insert into cards(id, card_type_id,
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
            card.active,)).lastrowid
        card._id = _card_id
        if self.store_pregenerated_data:
            self.con.execute(\
                "update cards set question=?, answer=?, tags=? where _id=?",
                (card.question("plain_text"), card.answer("plain_text"),
                card.tag_string(), _card_id))
        # Link card to its tags. The tags themselves have already been created
        # by default_controller calling get_or_create_tag_with_name.
        # Note: using executemany here is often slower here as cards mostly
        # have 0 or 1 tags.
        for tag in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (tag._id, _card_id))
        # Add card is not logged here, but in the controller, to make sure
        # that the first repetition is logged after the card creation.

    def card(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from cards where _id=?",
                                       (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from cards where id=?",
                                       (id, )).fetchone()
        fact = self.fact(sql_res["_fact_id"], id_is_internal=True)
        card_type = self.card_type_by_id(sql_res["card_type_id"])
        for fact_view in card_type.fact_views:
            if fact_view.id == sql_res["fact_view_id"]:
                card = Card(card_type, fact, fact_view,
                    creation_time=sql_res["creation_time"])
                break
        for attr in ("id", "_id", "grade", "next_rep", "last_rep", "easiness",
            "acq_reps", "ret_reps", "lapses", "acq_reps_since_lapse",
            "ret_reps_since_lapse", "modification_time", "scheduler_data",
            "active"):
            setattr(card, attr, sql_res[attr])
        self._get_extra_data(sql_res, card)
        for cursor in self.con.execute("""select _tag_id from tags_for_card
            where _card_id=?""", (sql_res["_id"], )):
            card.tags.add(self.tag(cursor["_tag_id"], id_is_internal=True))
        return card
    
    def update_card(self, card, repetition_only=False):
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

    def delete_card(self, card):
        self.con.execute("delete from cards where _id=?", (card._id, ))
        self.con.execute("delete from tags_for_card where _card_id=?",
            (card._id, ))
        for tag in card.tags:
            self.remove_tag_if_unused(tag)
        self.log().deleted_card(card)
        del card

    #
    # Fact views.
    #

    def add_fact_view(self, fact_view):
        _fact_view_id = self.con.execute("""insert into fact_views(id, name, q_fields,
            a_fields, a_on_top_of_q, type_answer, extra_data)
            values(?,?,?,?,?,?,?)""", (fact_view.id, fact_view.name,
            repr(fact_view.q_fields), repr(fact_view.a_fields),
            fact_view.a_on_top_of_q, fact_view.type_answer,
            self._repr_extra_data(fact_view.extra_data))).lastrowid
        fact_view._id = _fact_view_id
        self.log().added_fact_view(fact_view)

    def fact_view(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from fact_views where _id=?",
                (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from fact_views where id=?",
                 (id, )).fetchone()            
        fact_view = FactView(sql_res["name"], sql_res["id"])
        fact_view._id = sql_res["_id"]
        for attr in ("q_fields", "a_fields"):
            setattr(fact_view, attr, eval(sql_res[attr]))
        for attr in ["a_on_top_of_q", "type_answer"]:
            setattr(fact_view, attr, bool(sql_res[attr]))
        self._get_extra_data(sql_res, fact_view)
        return fact_view

    def update_fact_view(self, fact_view):
        self.con.execute("""update fact_views set name=?, q_fields=?,
            a_fields=?, a_on_top_of_q=?, type_answer=?, extra_data=? where
            _id=?""", (fact_view.name, repr(fact_view.q_fields),
            repr(fact_view.a_fields), fact_view.a_on_top_of_q,
            fact_view.type_answer, self._repr_extra_data(fact_view.extra_data),
            fact_view._id))
        self.log().edited_fact_view(fact_view)
        
    def delete_fact_view(self, fact_view):
        self.con.execute("delete from fact_views where _id=?",
            (fact_view._id, ))
        self.log().deleted_fact_view(fact_view)
        del fact_view
    
    #
    # Card types.
    #
        
    def add_card_type(self, card_type):
        self.con.execute("""insert into card_types(id, name, fields,
            unique_fields, required_fields, keyboard_shortcuts, extra_data)
            values (?,?,?,?,?,?,?)""", (card_type.id, card_type.name,
            repr(card_type.fields), repr(card_type.unique_fields),
            repr(card_type.required_fields),
            repr(card_type.keyboard_shortcuts),
            self._repr_extra_data(card_type.extra_data)))
        for fact_view in card_type.fact_views:
            # The fact views themselves have been added by the controller.
            # (Doing it here would upset the sync protocol.)
            self.con.execute("""insert into fact_views_for_card_type
                (_fact_view_id, card_type_id) values(?,?)""",
                (fact_view._id, card_type.id))
        self.component_manager.register(card_type)
        self.log().added_card_type(card_type)

    def card_type(self, id, id_is_internal):
        # Since there are so few of them, we don't use internal _ids.
        # ids should be unique too.
        if id in self.component_manager.card_type_by_id:
            return self.component_manager.card_type_by_id[id]
        parent_id, child_id = "", id
        if "::" in id:
            parent_id, child_id = id.rsplit("::", 1)
            parent = self.card_type(parent_id, id_is_internal=-1)
        else:
            parent = CardType(self.component_manager)
        sql_res = self.con.execute("select * from card_types where id=?",
                                   (id, )).fetchone()
        card_type = type(mangle(id), (parent.__class__, ),
            {"name": sql_res["name"], "id": id})(self.component_manager)
        for attr in ("fields", "unique_fields", "required_fields",
                     "keyboard_shortcuts"):
            setattr(card_type, attr, eval(sql_res[attr]))
        self._get_extra_data(sql_res, card_type)
        card_type.fact_views = []
        for cursor in self.con.execute("""select _fact_view_id from
            fact_views_for_card_type where card_type_id=?""", (id, )):
            card_type.fact_views.append(self.fact_view(\
                cursor["_fact_view_id"], id_is_internal=True))
        return card_type
        
    def update_card_type(self, card_type):
        self.con.execute("""update card_types set name=?, fields=?,
            unique_fields=?, required_fields=?, keyboard_shortcuts=?,
            extra_data=? where id=?""",
            (card_type.name, repr(card_type.fields),
            repr(card_type.unique_fields), repr(card_type.required_fields),
            repr(card_type.keyboard_shortcuts),
            self._repr_extra_data(card_type.extra_data), card_type.id))
        # Delete fact views and recreate them.
        for cursor in self.con.execute("""select _fact_view_id from
            fact_views_for_card_type where card_type_id=?""",
            (card_type.id, )):
            fact_view = self.fact_view(cursor[0], id_is_internal=True)
            self.delete_fact_view(fact_view)
        self.con.execute("""delete from fact_views_for_card_type where
            card_type_id=?""", (card_type.id, ))
        for fact_view in card_type.fact_views:
            self.add_fact_view(fact_view)
            self.con.execute("""insert into fact_views_for_card_type
                (_fact_view_id, card_type_id) values(?,?)""",
                (fact_view._id, card_type.id))
        self.component_manager.unregister(card_type)
        self.component_manager.register(card_type)
        self.log().edited_card_type(card_type)

    def delete_card_type(self, card_type):
        # The deletion of the fact views should happen at the controller
        # level, so as not to upset the sync protocol.
        self.con.execute("""delete from fact_views_for_card_type where
            card_type_id=?""", (card_type.id, ))
        self.con.execute("delete from card_types where id=?",
            (card_type.id, ))
        self.component_manager.unregister(card_type)
        self.log().deleted_card_type(card_type)
        del card_type

    #
    # Criteria.
    #

    def add_criterion(self, criterion):
        _id = self.con.execute("""insert into criteria (id, name, type, data)
            values(?,?,?,?)""", (criterion.id, criterion.name,
            criterion.criterion_type, criterion.data_to_string())).lastrowid
        criterion._id = _id
        # Only log the named criteria for syncing purposes.
        if criterion.name:
            self.log().added_criterion(criterion)
        
    def criterion(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from criteria where _id=?",
                (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from criteria where id=?",
                (id, )).fetchone()
        for criterion_class in \
            self.component_manager.all("criterion"):
            if criterion_class.criterion_type == sql_res["type"]:
                criterion = \
                    criterion_class(self.component_manager, sql_res["id"])
                criterion._id = sql_res["_id"]
                criterion.name = sql_res["name"]
                criterion.set_data_from_string(sql_res["data"])
                return criterion
    
    def update_criterion(self, criterion):
        self.con.execute("""update criteria set name=?, type=?, data=?
            where id=?""", (criterion.name, criterion.criterion_type,
            criterion.data_to_string(), criterion.id))
        if criterion._id == 1:
            self._current_criterion = criterion
        if criterion.name:
            self.log().edited_criterion(criterion)
        # Note that by design, the sync procedure never touches the current
        # criterion: you could have different cards active on different
        # devices.
 
    def delete_criterion(self, criterion):
        self.con.execute("delete from criteria where _id=?", (criterion._id, ))
        if criterion.name:
            self.log().deleted_criterion(criterion)
        del criterion
        
    def set_current_criterion(self, criterion):
        self.con.execute("update criteria set type=?, data=? where _id=1",
            (criterion.criterion_type, criterion.data_to_string()))
        self._current_criterion = criterion
        applier = self.component_manager.current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion)

    def current_criterion(self):
        return self._current_criterion
    
    def criteria(self):
        return (self.criterion(cursor[0], id_is_internal=True) \
            for cursor in self.con.execute("select _id from criteria"))
    
    #
    # Process media files in fact data.
    #

    def _media_hash(self, filename):

        """A hash function that will be used to determine whether or not a
        media file has been modified outside of Mnemosyne.

        'filename' is a relative path inside the media dir.

        In the current implementation, we use the modification date for this.
        Although less robust, modification dates are faster to lookup then
        calculating a hash, especially on mobile devices.

        In principle, you could have different hash implementations on
        different systems, as the hash is considered something internal and is
        not sent across during sync e.g.

        """
        
        return str(os.path.getmtime(os.path.join(self.media_dir(),
            os.path.normcase(filename))))
    
    def _process_media(self, fact):

        """Copy the media files to the media directory and edit the media
        table. We don't keep track of which facts use which media and delete
        a media file if it's no longer in use. The reason for this is that some
        people use the media directory as their only location to store their
        media files, and also use these files for other purposes.
        
        When we are applying log entries during sync, we should not generate
        extra log entries, this will be taken care of by the syncing
        algorithm. (Not all 'added_media' events originated here, they are
        also generated by the latex subsystem, or by checking for files which
        were modified outside of Mnemosyne.

        """

        for match in re_src.finditer("".join(fact.data.values())):
            filename = match.group(1)
            # If needed, copy file to the media dir. Normally this happens when
            # the user clicks 'Add image' e.g., but he could have typed in the
            # full path directly.
            if os.path.isabs(filename):
                filename = copy_file_to_dir(filename, self.media_dir())
            else:  # We always store Unix paths internally.
                filename = filename.replace("\\", "/")
            for key, value in fact.data.iteritems():
                fact.data[key] = value.replace(match.group(1), filename)
                self.con.execute("""update data_for_fact set value=? where
                    _fact_id=? and key=?""", (fact.data[key], fact._id, key))
            if self.con.execute("select count() from media where filename=?",
                                (filename, )).fetchone()[0] == 0:
                self.con.execute("""insert into media(filename, _hash)
                    values(?,?)""", (filename, self._media_hash(filename)))
                if not self.syncing:
                    self.log().added_media(filename)

    def clean_orphaned_media(self):
        import time
        import re
        t = time.time()
        re1 = re.compile(r"src=[\"'](.+?)[\"']", re.IGNORECASE)
        filenames = set()
        for result in self.con.execute("select value from data_for_fact where value like '%src=%'"):
            for match in re1.finditer(result[0]):
                filenames.add(match.group(1))
        print len(filenames)
        print time.time() - t
        print 'walk'
        import os

        for dirname, dirnames, filenames in os.walk(self.media_dir()):
            #for subdirname in dirnames:
            #    print os.path.join(dirname, subdirname)
            for filename in filenames:
                print filename


    #
    # Queries.
    #

    def cards_from_fact(self, fact):
        return list(self.card(cursor[0], id_is_internal=True) for cursor
            in self.con.execute("select _id from cards where _fact_id=?",
                                (fact._id, )))

    def count_sister_cards_with_next_rep(self, card, next_rep):
        return self.con.execute("""select count() from cards where
            next_rep=? and _id<>? and grade>=2 and _id in
            (select _id from cards where _fact_id=?)""",
            (next_rep, card._id, card.fact._id)).fetchone()[0]

    def duplicates_for_fact(self, fact, card_type):

        """Return facts with the same 'card_type.unique_fields'
        data as 'fact'.

        """

        _fact_ids = set()
        for field in card_type.unique_fields:
            if fact._id:
                for cursor in self.con.execute("""select _fact_id from
                    data_for_fact where key=? and value=?
                    and not _fact_id=?""", (field, fact[field], fact._id)):
                    _fact_ids.add(cursor[0])
            else:
                # The fact has not yet been saved in the database.
                for cursor in self.con.execute("""select _fact_id from
                    data_for_fact where key=? and value=?""",
                    (field, fact[field])):
                    _fact_ids.add(cursor[0])
        # Now we still need to make sure these facts are from cards with
        # the correct card type.
        facts = []
        for _fact_id in _fact_ids:
            this_card_type_id = self.con.execute("""select card_type_id
                from cards where _fact_id=?""", (_fact_id, )).fetchone()[0]
            if this_card_type_id == card_type.id:
                facts.append(self.fact(_fact_id, id_is_internal=True))
        return facts

    def card_types_in_use(self):
        return [self.card_type_by_id(cursor[0]) for cursor in \
            self.con.execute ("select distinct card_type_id from cards")]
    
    def tag_count(self):
        return self.con.execute("select count() from tags").fetchone()[0]
    
    def fact_count(self):
        return self.con.execute("select count() from facts").fetchone()[0]

    def card_count(self):
        return self.con.execute("""select count() from cards""").fetchone()[0]

    def non_memorised_count(self):
        return self.con.execute("""select count() from cards
            where active=1 and grade<2""").fetchone()[0]

    def scheduled_count(self, timestamp):
        count = self.con.execute("""select count() from cards
            where active=1 and grade>=2 and ?>=next_rep""",
            (timestamp, )).fetchone()[0]
        return count

    def active_count(self):
        return self.con.execute("""select count() from cards
            where active=1""").fetchone()[0]

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
        else:
            return sort_key

    def cards_due_for_ret_rep(self, timestamp, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade>=2 and ?>=next_rep order by %s limit ?"""
            % sort_key, (timestamp, limit)))
    
    def cards_due_for_final_review(self, grade, sort_key="", limit=-1):
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
            active=1 and grade>=2 and ?<next_rep order by %s limit ?"""
            % sort_key, (timestamp, limit)))

    #
    # Extra commands for custom schedulers.
    #
    
    def set_scheduler_data(self, scheduler_data):
        self.con.execute("update cards set scheduler_data=?",
            (scheduler_data, ))

    def cards_with_scheduler_data(self, scheduler_data, sort_key="", limit=-1):
        sort_key = self._process_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and scheduler_data=? order by %s limit ?"""
            % sort_key, (scheduler_data, limit)))

    def scheduler_data_count(self, scheduler_data):
        return self.con.execute("""select count() from cards
            where active=1 and scheduler_data=?""",
            (scheduler_data, )).fetchone()[0]        
