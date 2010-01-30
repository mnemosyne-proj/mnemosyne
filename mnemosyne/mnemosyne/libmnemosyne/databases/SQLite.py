#
# SQLite.py - Ed Bartosh <bartosh@gmail.com>, <Peter.Bienstman@UGent.be>
#

import os
import re
import sys
import time
import shutil
import sqlite3
import datetime

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import mangle, copy_file_to_dir
from mnemosyne.libmnemosyne.utils import expand_path, contract_path

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)

# All id's beginning with an underscore refer to primary keys in the SQL
# database. All other id's correspond to the id's used in libmnemosyne.
# We don't use libmnemosyne id's as primary keys for speed reasons
# (100 times slowdown in joins). We add indices on id's as well, since
# the is the only handle we have during the sync process.

# All times are Posix timestamps.

SCHEMA = """
    begin;
    
    create table facts(
        _id integer primary key,
        id text,
        card_type_id text,
        creation_time integer,
        modification_time integer,
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
        _fact_id integer,
        fact_view_id text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        last_rep integer,
        next_rep integer,
        extra_data text default "",
        scheduler_data integer default 0,
        active boolean default 1,
        in_view boolean default 1
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

    /* _id=1 is reserved for the currently active criteria, which could be a
    copy of another saved criterion or a completely different, unnamed
    criterion. */
    
    create table activity_criteria(
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
        _id integer primary key,
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
        scheduler_data integer
    );
    create index i_log_timestamp on log (timestamp);
    create index i_log_object_id on log (object_id);
    
    /* We track the last _id as opposed to the last timestamp, as importing
       another database could add log events with earlier dates, but
       which still need to be synced. */
    
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
        _fact_view_id text,
        card_type_id text
    );
    
    commit;
"""
        
from mnemosyne.libmnemosyne.databases.SQLite_sync import SQLiteSync
from mnemosyne.libmnemosyne.databases.SQLite_logging import SQLiteLogging
from mnemosyne.libmnemosyne.databases.SQLite_statistics import SQLiteStatistics

class SQLite(Database, SQLiteSync, SQLiteLogging, SQLiteStatistics):

    """Note that most of the time, Commiting is done elsewhere, e.g. by
    calling save in the main controller, in order to have a better control
    over transaction granularity.

    """

    version = "SQL 1.0"
    suffix = ".db"

    def __init__(self, component_manager):
        Database.__init__(self, component_manager)
        self._connection = None
        self._path = None # Needed for lazy creation of connection.
        self.load_failed = True
        self._current_criterion = None # Cached for performance reasons.

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
    
    def database_name(self):
        if not self.is_loaded():
            return None
        else:
            return os.path.basename(self.config()["path"]).\
                   split(self.database().suffix)[0]
        
    def mediadir(self):
        return os.path.join(self.config().basedir,
            os.path.basename(self.config()["path"]) + "_media")
    
    def new(self, path):
        if self.is_loaded():
            self.unload()
        self._path = expand_path(path, self.config().basedir)
        if os.path.exists(self._path):
            os.remove(self._path)
        self.load_failed = False
        # Create tables.
        self.con.executescript(SCHEMA)
        self.con.execute("insert into global_variables(key, value) values(?,?)",
                        ("version", self.version))
        self.con.execute("""insert into partnerships(partner, _last_log_id)
                         values(?,?)""", ("log.txt", 0))
        self.con.commit()
        self.config()["path"] = contract_path(self._path, self.config().basedir)
        # Create default criterion.
        from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
             DefaultCriterion
        self._current_criterion = DefaultCriterion(self.component_manager)
        self.add_activity_criterion(self._current_criterion)
        # Create media directory.
        mediadir = self.mediadir()
        if not os.path.exists(mediadir):
            os.mkdir(mediadir)

    def _find_plugin_for_card_type(self, card_type_id):
        found = False
        for plugin in self.plugins():
            for component in plugin.components:
                if component.component_type == "card_type" and \
                    component.id == card_type_id:
                    found = True
                    try:
                        plugin.activate()
                    except:
                        self._connection.close()
                        self._connection = None
                        self.load_failed = True
                        raise RuntimeError, _("Error when running plugin:") \
                            + "\n" + traceback_string()
        if not found:
            self._connection.close()
            self._connection = None
            self.load_failed = True
            raise RuntimeError, _("Missing plugin for card type with id:") \
                + " " + card_type_id

    def load(self, path):
        if self.is_loaded():
            self.unload()
        self._path = expand_path(path, self.config().basedir)
        # Check database version.
        try:
            sql_res = self.con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
            self.load_failed = False
        except sqlite3.OperationalError:
            self.main_widget().error_box(
                _("Another copy of Mnemosyne is still running.") + "\n" +
                _("Continuing is impossible and will lead to data loss!"))
            sys.exit()
        except:
            self.load_failed = True
            raise RuntimeError, _("Unable to load file.")
        
        if sql_res["value"] != self.version:
            self.load_failed = True
            raise RuntimeError, \
                _("Unable to load file: database version mismatch.")
        # Instantiate card types stored in this database.
        for cursor in self.con.execute("select id from card_types"):
            id = cursor[0]
            card_type = self.get_card_type(id, id_is_internal=-1)
            self.component_manager.register(card_type)
        # Identify missing plugins for card types and their parents.       
        plugin_needed = set()
        active_ids = set(card_type.id for card_type in self.card_types())
        for cursor in self.con.execute("""select distinct card_type_id
            from facts"""):
            id = cursor[0]
            while "::" in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit("::", 1)
                if id not in active_ids:
                    plugin_needed.add(id)
            if id not in active_ids:
                plugin_needed.add(id)
        for card_type_id in plugin_needed:
            self._find_plugin_for_card_type(card_type_id)
        self._current_criterion = self.get_activity_criterion\
            (1, id_is_internal=True)
        self.config()["path"] = contract_path(path, self.config().basedir)
        for f in self.component_manager.get_all("hook", "after_load"):
            f.run()
        # We don't log the database load here, as we prefer to log the start
        # of the program first.
        
    def save(self, path=None):
        # Don't erase a database which failed to load.
        if self.load_failed == True:
            return -1
        # Update format.
        self.con.execute("update global_variables set value=? where key=?",
                         (self.version, "version" ))
        # Save database and copy it to different location if needed.
        self.con.commit()
        if not path:
            return
        dest_path = expand_path(path, self.config().basedir)
        if dest_path != self._path:
            shutil.copy(self._path, dest_path)
            self._path = dest_path
        self.config()["path"] = contract_path(path, self.config().basedir)
        # We don't log every save, as that would result in an event after
        # every review.

    def backup(self):
        self.save()
        if self.config()["backups_to_keep"] == 0:
            return
        backupdir = os.path.join(self.config().basedir, "backups")
        # Make a copy. Create only a single file per day.
        db_name = os.path.basename(self._path).rsplit(".", 1)[0]
        backupfile = db_name + "-" + \
                   datetime.datetime.today().strftime("%Y%m%d-%H:%M.db")
        backupfile = os.path.join(backupdir, backupfile)
        shutil.copy(self._path, backupfile)
        if not os.path.exists(backupfile) or not os.stat(backupfile).st_size:
            self.main_widget().information_box(\
                _("Warning: backup creation failed for") + " " +  backupfile)
        for f in self.component_manager.get_all("hook", "after_backup"):
            f.run(backupfile)
        # Only keep the last logs.
        if self.config()["backups_to_keep"] < 0:
            return backupfile
        files = [f for f in os.listdir(backupdir) \
                if f.startswith(db_name + "-")]
        files.sort()
        if len(files) > self.config()["backups_to_keep"]:
            surplus = len(files) - self.config()["backups_to_keep"]
            for file in files[0:surplus]:
                os.remove(os.path.join(backupdir, file))
        return backupfile

    def unload(self):
        for f in self.component_manager.get_all("hook", "before_unload"):
            f.run()
        self.log().dump_to_txt_log()
        if self._connection:
            self.save()
            self._connection.close()
            self._connection = None
        self._path = None
        self.load_failed = True
        return True

    def abandon(self):
        if self._connection:        
            self._connection.close()
            self._connection = None
        self._path = None
        self.load_failed = True        
        
    def is_loaded(self):
        return not self.load_failed

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
        sql_res = self.con.execute("""select * from tags where name=?""",
                                   (name, )).fetchone()
        if sql_res:
            tag = Tag(sql_res["name"], sql_res["id"])
            tag._id = sql_res["_id"]
            self._get_extra_data(sql_res, tag)
        else:
            tag = Tag(name)
            self.add_tag(tag)
        return tag

    def add_tag(self, tag, timestamp=None):
        # We can specify the timestamp at which this event happened.
        # Needed during synchronisation process.
        _id = self.con.execute("""insert into tags(name, extra_data, id)
            values(?,?,?)""", (tag.name,
            self._repr_extra_data(tag.extra_data), tag.id)).lastrowid
        tag._id = _id
        if not timestamp:
            timestamp = int(time.time())
        self.log_added_tag(timestamp, tag.id)
        for criterion in self.get_activity_criteria():
            criterion.tag_created(tag)
            self.update_activity_criterion(criterion)

    def get_tag(self, id, id_is_internal):
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

    def update_tag(self, tag, timestamp=None):
        self.con.execute("update tags set name=?, extra_data=? where _id=?",
            (tag.name, self._repr_extra_data(tag.extra_data),
             tag._id))
        if not timestamp:
            timestamp = time.time()
        self.log_updated_tag(timestamp, tag.id)
    
    def delete_tag(self, tag, timestamp=None):
        self.con.execute("delete from tags where _id=?", (tag._id, ))
        if not timestamp:
            timestamp = time.time()
        self.log_deleted_tag(timestamp, tag.id)
        for criterion in self.get_activity_criteria():
            criterion.tag_deleted(tag)
            self.update_activity_criterion(criterion)
        del tag
        
    def remove_tag_if_unused(self, tag):
        if self.con.execute("""select count() from tags as cat,
            tags_for_card as cat_c where cat_c._tag_id=cat._id and
            cat._id=?""", (tag._id, )).fetchone()[0] == 0:
            self.delete_tag(tag)
            
    def get_tags(self):
        return (self.get_tag(cursor[0], id_is_internal=True) for cursor in \
            self.con.execute("select _id from tags"))
    
    def get_tag_names(self):
        return [cursor[0] for cursor in \
                self.con.execute("select name from tags")]
    
    #
    # Facts.
    #
    
    def add_fact(self, fact, timestamp=None):
        self.load_failed = False
        # Add fact to facts table.
        _fact_id = self.con.execute("""insert into facts(id, card_type_id,
            creation_time, modification_time) values(?,?,?,?)""",
            (fact.id, fact.card_type.id, fact.creation_time,
             fact.modification_time)).lastrowid
        fact._id = _fact_id
        # Create data_for_fact.        
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((_fact_id, key, value)
                for key, value in fact.data.items()))
        if not timestamp:
            timestamp = time.time()
        self.log_added_fact(timestamp, fact.id)
        # Process media files.
        self._process_media(fact, timestamp)

    def get_fact(self, id, id_is_internal):
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
        fact = Fact(data, self.card_type_by_id(sql_res["card_type_id"]),
            creation_time=sql_res["creation_time"], id=sql_res["id"])
        fact._id = sql_res["_id"]
        fact.modification_time = sql_res["modification_time"]
        self._get_extra_data(sql_res, fact)
        return fact
    
    def update_fact(self, fact, timestamp=None):
        # Update fact.
        self.con.execute("""update facts set card_type_id=?, creation_time=?,
            modification_time=? where _id=?""", (fact.card_type.id,
            fact.creation_time, fact.modification_time, fact._id))
        # Delete data_for_fact and recreate it.
        self.con.execute("delete from data_for_fact where _fact_id=?",
            (fact._id, ))
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((fact._id, key, value)
                for key, value in fact.data.items()))
        if not timestamp:
            timestamp = time.time()
        self.log_updated_fact(timestamp, fact.id)
        # Process media files.
        self._process_media(fact, timestamp)        

    def delete_fact_and_related_data(self, fact, timestamp=None):
        for card in self.cards_from_fact(fact):
            self.delete_card(card)
        self.con.execute("delete from facts where _id=?", (fact._id, ))
        self.con.execute("delete from data_for_fact where _fact_id=?",
                         (fact._id, ))
        if not timestamp:
            timestamp = time.time()
        self.log_deleted_fact(timestamp, fact.id)
        del fact

    #
    # Cards.
    #
    
    def add_card(self, card):
        self.load_failed = False
        _card_id = self.con.execute("""insert into cards(id, _fact_id,
            fact_view_id, grade, easiness, acq_reps, ret_reps, lapses,
            acq_reps_since_lapse, ret_reps_since_lapse, last_rep, next_rep,
            extra_data, scheduler_data, active, in_view)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (card.id, card.fact._id, card.fact_view.id, card.grade,
            card.easiness, card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            card.last_rep, card.next_rep,
            self._repr_extra_data(card.extra_data),
            card.scheduler_data, card.active, card.in_view)).lastrowid
        card._id = _card_id
        # Link card to its tags. The tags themselves have already been created
        # by default_controller calling get_or_create_tag_with_name.
        # Note: using executemany here is often slower here as cards mostly
        # have 0 or 1 tags.
        for tag in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (tag._id, _card_id))
        # Add card is not logged here, but in the controller, to make sure
        # that the first repetition is logged after the card creation.

    def get_card(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute("select * from cards where _id=?",
                                       (id, )).fetchone()
        else:
            sql_res = self.con.execute("select * from cards where id=?",
                                       (id, )).fetchone()            
        fact = self.get_fact(sql_res["_fact_id"], id_is_internal=True)
        for fact_view in fact.card_type.fact_views:
            if fact_view.id == sql_res["fact_view_id"]:
                card = Card(fact, fact_view)
                break
        for attr in ("id", "_id", "grade", "easiness", "acq_reps", "ret_reps",
            "lapses", "acq_reps_since_lapse", "ret_reps_since_lapse",
            "last_rep", "next_rep", "scheduler_data", "active", "in_view"):
            setattr(card, attr, sql_res[attr])
        self._get_extra_data(sql_res, card)
        for cursor in self.con.execute("""select _tag_id from tags_for_card
            where _card_id=?""", (sql_res["_id"], )):
            card.tags.add(self.get_tag(cursor["_tag_id"], id_is_internal=True))
        return card
    
    def update_card(self, card, repetition_only=False, timestamp=None):
        self.con.execute("""update cards set _fact_id=?, fact_view_id=?,
            grade=?, easiness=?, acq_reps=?, ret_reps=?, lapses=?,
            acq_reps_since_lapse=?, ret_reps_since_lapse=?, last_rep=?,
            next_rep=?, extra_data=?, scheduler_data=?, active=?,
            in_view=? where _id=?""",
            (card.fact._id, card.fact_view.id, card.grade, card.easiness,
            card.acq_reps, card.ret_reps, card.lapses,
            card.acq_reps_since_lapse, card.ret_reps_since_lapse,
            card.last_rep, card.next_rep,
            self._repr_extra_data(card.extra_data),
            card.scheduler_data, card.active, card.in_view, card._id))
        if not timestamp:
            timestamp = time.time()
        self.log_updated_card(timestamp, card.id)
        if repetition_only:
            return
        # Link card to its tags. The tags themselves have already been created
        # by default_controller calling get_or_create_tag_with_name.
        # Unused tags will also be cleaned up there.
        self.con.execute("delete from tags_for_card where _card_id=?",
                         (card._id, ))
        for tag in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (tag._id, card._id))

    def delete_card(self, card, timestamp=None):
        self.con.execute("delete from cards where _id=?", (card._id, ))
        self.con.execute("delete from tags_for_card where _card_id=?",
                         (card._id, ))
        for tag in card.tags:
            self.remove_tag_if_unused(tag)
        if not timestamp:
            timestamp = time.time()     
        self.log_deleted_card(timestamp, card.id)
        del card

    #
    # Fact views.
    #

    def _add_fact_view(self, fact_view):
        return self.con.execute("""insert into fact_views(id, name, q_fields,
            a_fields, a_on_top_of_q, type_answer, extra_data)
            values(?,?,?,?,?,?,?)""", (fact_view.id, fact_view.name,
            repr(fact_view.q_fields), repr(fact_view.a_fields),
            fact_view.a_on_top_of_q, fact_view.type_answer,
            self._repr_extra_data(fact_view.extra_data))).lastrowid

    def _get_fact_view(self, _id):
        sql_res = self.con.execute("select * from fact_views where _id=?",
                                   (_id, )).fetchone()
        fact_view = FactView(sql_res["id"], sql_res["name"])
        for attr in ("q_fields", "a_fields"):
            setattr(fact_view, attr, eval(sql_res[attr]))
        for attr in ["a_on_top_of_q", "type_answer"]:
            setattr(fact_view, attr, sql_res[attr])
        self._get_extra_data(sql_res, fact_view)
        return fact_view
    
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
            _fact_view_id = self._add_fact_view(fact_view)
            self.con.execute("""insert into fact_views_for_card_type
                (_fact_view_id, card_type_id) values(?,?)""",
                (_fact_view_id, card_type.id))
        self.log().added_card_type(card_type)

    def get_card_type(self, id, id_is_internal):
        # There are no internal ids for card types.
        if id in self.component_manager.card_type_by_id:
            return self.component_manager.card_type_by_id[id]
        parent_id, child_id = "", id
        if "::" in id:
            parent_id, child_id = id.rsplit("::", 1)
            parent = self.get_card_type(parent_id, id_is_internal=-1)
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
            card_type.fact_views.append(self._get_fact_view(\
                cursor["_fact_view_id"]))
        return card_type
        
    def update_card_type(self, card_type):
        self.con.execute("""update card_types set name=?, fields=?,
            unique_fields=?, required_fields=?, keyboard_shortcuts=?,
            extra_data=? where id=?""",
            (card_type.name, repr(card_type.fields),
            repr(card_type.unique_fields), repr(card_type.required_fields),
            repr(card_type.keyboard_shortcuts),
            self._repr_extra_data(card_type.extra_data), card_type.id))
        self.con.execute("""delete from fact_views where _id in (select
            _fact_view_id from fact_views_for_card_type where
            card_type_id=?)""", (card_type.id, ))
        self.con.execute("""delete from fact_views_for_card_type where
            card_type_id=?""", (card_type.id, ))
        for fact_view in card_type.fact_views:
            _fact_view_id = self._add_fact_view(fact_view)
            self.con.execute("""insert into fact_views_for_card_type
                (_fact_view_id, card_type_id) values(?,?)""",
                (_fact_view_id, card_type.id))
        self.log().updated_card_type(card_type)

    def delete_card_type(self, card_type):
        self.con.execute("""delete from fact_views where _id in (select
            _fact_view_id from fact_views_for_card_type where
            card_type_id=?)""", (card_type.id, ))
        self.con.execute("""delete from fact_views_for_card_type where
            card_type_id=?""", (card_type.id, ))
        self.con.execute("delete from card_types where id=?",
            (card_type.id, ))
        self.log().deleted_card_type(card_type)       

    #
    # Activity criteria.
    #

    def add_activity_criterion(self, criterion):
        _id = self.con.execute("""insert into activity_criteria
            (id, name, type, data) values(?,?,?,?)""", (criterion.id,
            criterion.name, criterion.criterion_type,
            criterion.data_to_string())).lastrowid
        criterion._id = _id
            
    def get_activity_criterion(self, id, id_is_internal):
        if id_is_internal:
            sql_res = self.con.execute(\
                "select * from activity_criteria where _id=?",
                (id, )).fetchone()
        else:
            sql_res = self.con.execute(\
                "select * from activity_criteria where id=?",
                (id, )).fetchone()
        for criterion_class in \
            self.component_manager.get_all("activity_criterion"):
            if criterion_class.criterion_type == sql_res["type"]:
                criterion = criterion_class(self.component_manager,
                                            sql_res["id"])
                criterion._id = sql_res["_id"]
                criterion.name = sql_res["name"]
                criterion.data_from_string(sql_res["data"])
                return criterion
    
    def update_activity_criterion(self, criterion):
        self.con.execute("""update activity_criteria set name=?, type=?, data=?
            where id=?""", (criterion.name, criterion.criterion_type,
            criterion.data_to_string(), criterion.id))
        if criterion._id == 1:
            self._current_criterion = criterion
 
    def delete_activity_criterion(self, criterion):
        self.con.execute("delete from activity_criteria where _id=?",
            (criterion._id, ))
        del criterion
    
    def set_current_activity_criterion(self, criterion):
        self.con.execute("""update activity_criteria set type=?, data=?
            where _id=1""", (criterion.criterion_type, criterion.data_to_string()))
        self._current_criterion = criterion
        applier = self.component_manager.get_current("criterion_applier",
            used_for=criterion.__class__)
        applier.apply_to_database(criterion, active_or_in_view=applier.ACTIVE)

    def current_activity_criterion(self):
        return self._current_criterion
    
    def get_activity_criteria(self):
        return (self.get_activity_criterion(cursor[0], id_is_internal=True) \
            for cursor in self.con.execute(\
                "select _id from activity_criteria"))
    
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
        
        return str(os.path.getmtime(os.path.join(self.mediadir(),
            os.path.normcase(filename))))
    
    def _process_media(self, fact, timestamp):

        """Copy the media files to the media directory and update the media
        table. We don't keep track of which facts use which media and delete
        a media file if it's no longer in use. The reason for this is that some
        people use the media directory as their only location to store their
        media files, and also use these files for other purposes.

        """
                
        for match in re_src.finditer("".join(fact.data.values())):
            filename = match.group(1)
            # If needed, copy file to the media dir. Normally this happens when
            # the user clicks 'Add image' e.g., but he could have typed in the
            # full path directly.
            if os.path.isabs(filename):
                filename = copy_file_to_dir(filename, self.mediadir())
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
                self.log_added_media(timestamp, filename)
    
    #
    # Queries.
    #

    def cards_from_fact(self, fact):
        return list(self.get_card(cursor[0], id_is_internal=True) for cursor
            in self.con.execute("select _id from cards where _fact_id=?",
                                (fact._id, )))

    def count_related_cards_with_next_rep(self, card, next_rep):
        return self.con.execute("""select count() from cards where
            next_rep=? and _id<>? and grade>=2 and _id in
            (select _id from cards where _fact_id=?)""",
            (next_rep, card._id, card.fact._id)).fetchone()[0]

    def duplicates_for_fact(self, fact):

        """Return fact with the same 'unique_fields' data as 'fact'."""
        
        query = "select _id from facts where card_type_id=?"
        args = (fact.card_type.id,)
        if fact._id:
            query += " and not _id=?"
            args = (fact.card_type.id, fact._id)
        duplicates = []            
        for cursor in self.con.execute(query, args):
            data = dict([(cursor2["key"], cursor2["value"]) for cursor2 in \
                self.con.execute("""select * from data_for_fact where
                _fact_id=?""", (cursor[0], ))])
            for field in fact.card_type.unique_fields:
                if data[field] == fact[field]:
                    duplicates.append(\
                        self.get_fact(cursor[0], id_is_internal=True))
                    break
        return duplicates

    def card_types_in_use(self):
        return [self.card_type_by_id(cursor[0]) for cursor in \
            self.con.execute ("select distinct card_type_id from facts")]

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
