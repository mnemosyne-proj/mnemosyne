#
# sqlite.py - Ed Bartosh <bartosh@gmail.com>, <Peter.Bienstman@UGent.be>
#

import os
import time
import shutil
import sqlite3

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import expand_path, contract_path

# Note: all id's beginning with an underscore refer to primary keys in the
# SQL database. All other id's correspond to the id's used in libmnemosyne.
# We don't use libmnemosyne id's as primary keys for speed reasons.

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

    create table tags(
        _id integer primary key,
        _parent_key integer default 0,
        id text,
        name text,
        extra_data text default ""
    );

    create table tags_for_card(
        _card_id integer,
        _tag_id integer
    );
    create index i_tags_for_card on tags_for_card (_card_id);

    create table global_variables(
        key text,
        value text
    );

    /* For object_id, we need to store the full ids as opposed to the _ids.
       When deleting an object, there is no longer a way to get the ids from
       the _ids, and for robustness and interoperability, we need to send the
       ids across when syncing.
    */
       
    create table history(
        _id integer primary key,
        event integer,
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
        thinking_time integer
    );
    create index i_history on history (timestamp);

    /* We track the last _id as opposed to the last timestamp, as importing
       another database could add history events with earlier dates, but
       which still need to be synced. */
    
    create table partnerships(
        partner text,
        _last_history_id integer
    );

    create table media(
        filename text,
        _fact_id integer,
        last_modified integer
    );

    /* Here, we store the card types that are created at run time by the user
       through the GUI, as opposed to those that are instantiated through a
       plugin. For columns containing lists and lists of tuples like 'fields',
       'unique_fields', ... we store the __repr__ representations of the
       Python objects.
    */

    create table fact_views(
        id text,
        name text,
        q_fields text,
        a_fields text,
        required_fields text,
        a_on_top_of_q boolean default 0
    );

    create table card_types(
        id text,
        parent text, /* Name of the parent class. */
        name text,
        fields text,
        unique_fields text,
        keyboard_shortcuts text
    );

    create table fact_views_for_card_type(
        fact_view_id text,
        card_type_id text
    );
    
    commit;
"""


class SQLite(Database):

    version = "SQL 1.0"
    suffix = ".db"

    def __init__(self, component_manager):
        Database.__init__(self, component_manager)
        self._connection = None
        self._path = None # Needed for lazy creation of connection.
        self.load_failed = True

    @property
    def con(self):
        
        """Connection to the database, lazily created."""

        if not self._connection:
            self._connection = sqlite3.connect(self._path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def new(self, path):
        if self.is_loaded():
            self.unload()
        self._path = expand_path(path, self.config().basedir)
        if os.path.exists(self._path):
            os.remove(self._path)
        self.load_failed = False      
        self.con.executescript(SCHEMA) # Create tables.
        self.con.execute("insert into global_variables(key, value) values(?,?)",
                        ("version", self.version))
        self.con.execute("insert into global_variables(key, value) values(?,?)",
                        ("times_loaded", 0))
        self.con.execute("""insert into partnerships(partner, _last_history_id)
                         values(?,?)""", ("log.txt", 0))
        self.con.commit()
        self.config()["path"] = contract_path(self._path, self.config().basedir)

    def load(self, path):
        if self.is_loaded():        
            self.unload()
        self._path = expand_path(path, self.config().basedir)

        # Check database version.
        try:
            sql_res = self.con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
            self.load_failed = False
        except:
            self.load_failed = True
            raise RuntimeError, _("Unable to load file.")
        
        if sql_res["value"] != self.version:
            self.load_failed = True
            raise RuntimeError, \
                _("Unable to load file: database version mismatch.")

        # Vacuum database from time to time.
        sql_res = self.con.execute("""select value from global_variables
            where key=?""", ("times_loaded", )).fetchone()
        times_loaded = int(sql_res["value"]) + 1
        if times_loaded >= 5 and not self.config().resource_limited:
            self.con.execute("vacuum")
            times_loaded = 0
        self.con.execute("""update global_variables set value=? where
            key=?""", (str(times_loaded), "times_loaded"))

        # Deal with clones and plugins, also plugins for parent classes.
        plugin_needed = set()
        clone_needed = []
        active_id = set(card_type.id for card_type in self.card_types())
        for cursor in self.con.execute("""select distinct card_type_id
            from facts"""):
            id = cursor[0]
            while "." in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit(".", 1)          
                if id.endswith("_CLONED"):
                    id = id.replace("_CLONED", "")
                    clone_needed.append((id, child_name))
                if id not in active_id:
                    plugin_needed.add(id)
            if id not in active_id:
                plugin_needed.add(id)

        # Activate necessary plugins.
        for card_type_id in plugin_needed:
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
                            raise RuntimeError, \
                                  _("Error when running plugin:") \
                                  + "\n" + traceback_string()
            if not found:
                self._connection.close()
                self._connection = None
                self.load_failed = True
                raise RuntimeError, \
                      _("Missing plugin for card type with id:") \
                      + " " + card_type_id
            
        # Create necessary clones.
        for parent_type_id, clone_name in clone_needed:
            parent_instance = self.card_type_by_id(parent_type_id)
            try:
                parent_instance.clone(clone_name)
            except NameError:
                # In this case the clone was already created by loading the
                # database earlier.
                pass        
        self.config()["path"] = contract_path(path, self.config().basedir)
        for f in self.component_manager.get_all("function_hook", "after_load"):
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
        if self.config().resource_limited:
            return
        
        # TODO: wait for XML export format.
        # TODO: skip for resource limited?
        pass

    def unload(self):
        self.backup()
        self.log().dump_to_txt_log()
        if self._connection:
            self.save()
            self._connection.close()
            self._connection = None
        self._path = None
        self.load_failed = True
        return True
        
    def is_loaded(self):
        return not self.load_failed

    # Adding, modifying and deleting tags, facts and cards. Commiting is
    # done by calling save in the main controller, in order to have a better
    # control over transaction granularity.

    def _repr_extra_data(self, extra_data):
        if extra_data == {}:
            return "" # Save space.
        else:
            return repr(extra_data)

    def add_tag(self, tag):
        _id = self.con.execute("""insert into tags(name, extra_data, id)
            values(?,?,?)""", (tag.name,
            self._repr_extra_data(tag.extra_data), tag.id)).lastrowid
        tag._id = _id
        self.log().added_tag(tag)
        
    def delete_tag(self, tag):
        self.con.execute("delete from tags where _id=?", (tag._id,))
        self.log().deleted_tag(tag)
        del tag
        
    def update_tag(self, tag):
        self.con.execute("update tags set name=?, extra_data=? where _id=?",
            (tag.name, self._repr_extra_data(tag.extra_data),
             tag._id))
        self.log().updated_tag(tag)
        
    def get_or_create_tag_with_name(self, name):
        sql_res = self.con.execute("""select * from tags where name=?""",
                                   (name, )).fetchone()
        if sql_res:
            tag = Tag(sql_res["name"], sql_res["id"])
            tag._id = sql_res["_id"]
            return tag
        tag = Tag(name)
        self.add_tag(tag)
        return tag
    
    def remove_tag_if_unused(self, tag):
        if self.con.execute("""select count() from tags as cat,
            tags_for_card as cat_c where cat_c._tag_id=cat._id and
            cat._id=?""", (tag._id, )).fetchone()[0] == 0:
            self.delete_tag(tag)
    
    def add_fact(self, fact):
        self.load_failed = False
        # Add fact to facts and data_for_fact tables.
        _fact_id = self.con.execute("""insert into facts(id, card_type_id,
            creation_time, modification_time) values(?,?,?,?)""",
            (fact.id, fact.card_type.id, fact.creation_time,
             fact.modification_time)).lastrowid
        fact._id = _fact_id
        # Create data_for_fact.        
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((_fact_id, key, value)
                for key, value in fact.data.items()))
        self.log().added_fact(fact)

    def update_fact(self, fact):
        # Update fact.
        self.con.execute("""update facts set id=?, card_type_id=?,
            creation_time=?, modification_time=? where _id=?""",
            (fact.id, fact.card_type.id, fact.creation_time,
             fact.modification_time, fact._id))
        # Delete data_for_fact and recreate it.
        self.con.execute("delete from data_for_fact where _fact_id=?",
                (fact._id, ))
        self.con.executemany("""insert into data_for_fact(_fact_id, key, value)
            values(?,?,?)""", ((fact._id, key, value)
                for key, value in fact.data.items()))
        self.log().updated_fact(fact)
        
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
        # Link card to its tags.
        # The tags themselves have already been created by
        # default_main_controller calling get_or_create_tag_with_name.
        for cat in card.tags:
            _tag_id = self.con.execute("""select _id from tags
                where id=?""", (cat.id, )).fetchone()[0]
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (_tag_id, _card_id))
        # Add card is not logged here, but in the controller, to make sure
        # that the first repetition is logged after the card creation.

    def update_card(self, card, repetition_only=False):
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
        if repetition_only:
            return
        # Link card to its tags.
        # The tags themselves have already been created by
        # default_main_controller calling get_or_create_tag_with_name.
        self.con.execute("delete from tags_for_card where _card_id=?",
                         (card._id, ))
        for cat in card.tags:
            self.con.execute("""insert into tags_for_card(_tag_id,
                _card_id) values(?,?)""", (cat._id, card._id))
        self.log().updated_card(card)

    def delete_fact_and_related_data(self, fact):
        for card in self.cards_from_fact(fact):
            self.delete_card(card)
        self.con.execute("delete from facts where _id=?", (fact._id, ))
        self.con.execute("delete from data_for_fact where _fact_id=?",
                         (fact._id, ))
        self.log().deleted_fact(fact)
        del fact
        
    def delete_card(self, card):
        self.con.execute("delete from cards where _id=?", (card._id, ))
        self.con.execute("delete from tags_for_card where _card_id=?",
                         (card._id, ))
        for tag in card.tags:
            self.remove_tag_if_unused(tag)      
        self.log().deleted_card(card)
        del card

    # Retrieve tags, facts and cards using their internal id.

    def get_tag(self, _id):
        sql_res = self.con.execute("""select * from tags where _id=?""",
                                   (_id, )).fetchone()
        tag = Tag(sql_res["name"], sql_res["id"])
        tag._id = sql_res["_id"]
        return tag
    
    def get_fact(self, _id):        
        sql_res = self.con.execute("select * from facts where _id=?",
                                   (_id, )).fetchone()
        # Create dictionary with fact.data.
        data = dict([(cursor["key"], cursor["value"]) for cursor in
            self.con.execute("select * from data_for_fact where _fact_id=?",
            (_id, ))])
        # Create fact.
        fact = Fact(data, self.card_type_by_id(sql_res["card_type_id"]),
            creation_time=sql_res["creation_time"], id=sql_res["id"])
        fact._id = sql_res["_id"]
        fact.modification_time = sql_res["modification_time"]
        return fact

    def get_card(self, _id):
        sql_res = self.con.execute("select * from cards where _id=?",
                                   (_id, )).fetchone()
        fact = self.get_fact(sql_res["_fact_id"])
        for view in fact.card_type.fact_views:
            if view.id == sql_res["fact_view_id"]:
                card = Card(fact, view)
                break
        for attr in ("id", "_id", "grade", "easiness", "acq_reps", "ret_reps",
            "lapses", "acq_reps_since_lapse", "ret_reps_since_lapse",
            "last_rep", "next_rep", "scheduler_data", "active", "in_view"):
            setattr(card, attr, sql_res[attr])
        if sql_res["extra_data"] == "":
            card.extra_data = {}
        else:
            card.extra_data = eval(sql_res["extra_data"])
        for cursor in self.con.execute("""select cat.* from tags as cat,
            tags_for_card as cat_c where cat_c._tag_id=cat._id
            and cat_c._card_id=?""", (sql_res["_id"],)):
            tag = Tag(cursor["name"], cursor["id"])
            tag._id = cursor["_id"]
            card.tags.add(tag)              
        return card

    # Activate cards.
    
    def set_cards_active(self, card_types_fact_views, tags):
        return self._turn_on_cards("active", card_types_fact_views,
                                   tags)
    
    def set_cards_in_view(self, card_types_fact_views, tags):
        return self._turn_on_cards("in_view", card_types_fact_views,
                                   tags)
    
    def _turn_on_cards(self, attr, card_types_fact_views, tags):
        # Turn off everything.
        self.con.execute("update cards set active=0")
        # Turn on as soon as there is one active tag.
        command = """update cards set %s=1 where _id in (select cards._id
            from cards, tags, tags_for_card where
            tags_for_card._card_id=cards._id and
            tags_for_card._tag_id=tags._id and """ % attr
        args = []
        for cat in tags:
            command += "tags.id=? or "
            args.append(cat.id)
        command = command.rsplit("or ", 1)[0] + ")"
        self.con.execute(command, args)
        # Turn off inactive card types and views.
        command = """update cards set %s=0 where _id in (select cards._id
            from cards, facts where cards._fact_id=facts._id and """ % attr
        args = []        
        for card_type, fact_view in card_types_fact_views:
            command += "not (cards.fact_view_id=? and facts.card_type_id=?)"
            command += " and "
            args.append(fact_view.id)  
            args.append(card_type.id)          
        command = command.rsplit("and ", 1)[0] + ")"
        self.con.execute(command, args)

    # Queries.

    def tag_names(self):
        return list(cursor[0] for cursor in \
            self.con.execute("select name from tags"))

    def cards_from_fact(self, fact):
        return list(self.get_card(cursor[0]) for cursor in
            self.con.execute("select _id from cards where _fact_id=?",
                             (fact._id, )))

    def count_related_cards_with_next_rep(self, card, next_rep):
        return self.con.execute("""select count() from cards where
            next_rep=? and _id<>? and grade>=2 and _id in
            (select _id from cards where _fact_id=?)""",
            (next_rep, card._id, card.fact._id)).fetchone()[0]
    
    def has_fact_with_data(self, fact_data, card_type):
        fact_ids = set()
        for key, value in fact_data.items():
            # If key and value from fact_data are not in the database,
            # we don't have such a fact.
            if not self.con.execute("""select count() from data_for_fact, facts
                where data_for_fact.key=? and data_for_fact.value=? and
                facts._id=data_for_fact._fact_id and facts.card_type_id=?""",
                (key, value, card_type.id)).fetchone()[0]:
                return False
            # If they are present, then we still need to check that they
            # belong to the same fact.
            item_fact_ids = set((cursor["_fact_id"] for cursor in
                self.con.execute("""select _fact_id from data_for_fact, facts
                where data_for_fact.key=? and data_for_fact.value=? and
                facts._id=data_for_fact._fact_id and facts.card_type_id=?""",
                (key, value, card_type.id))))            
            if not fact_ids:
                fact_ids = item_fact_ids
            else:
                fact_ids = fact_ids.intersection(item_fact_ids)
            if not fact_ids:
                return False
        return True

    def duplicates_for_fact(self, fact):
        duplicates = []
        for cursor in self.con.execute("""select _id from facts
            where card_type_id=? and not _id=?""",
            (fact.card_type.id, fact._id)):
            data = dict([(cursor2["key"], cursor2["value"]) for cursor2 in \
                self.con.execute("""select * from data_for_fact where
                _fact_id=?""", (cursor[0], ))])
            for field in fact.card_type.unique_fields:
                if data[field] == fact[field]:
                    duplicates.append(self.get_fact(cursor[0]))
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
            (timestamp,)).fetchone()[0]
        return count

    def active_count(self):
        return self.con.execute("""select count() from cards
            where active=1""").fetchone()[0]

    def average_easiness(self):
        average = self.con.execute("""select sum(easiness)/count()
            from cards where easiness>0""").fetchone()[0]
        if average:
            return average
        else:
            return 2.5

    # Card queries used by the scheduler.
    
    def _parse_sort_key(self, sort_key):
        if sort_key == "":
            return "_id"
        if sort_key == "random":
            return "random()"
        if sort_key == "interval":
            return "next_rep - last_rep"
        return sort_key

    def cards_due_for_ret_rep(self, timestamp, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade>=2 and ?>=next_rep order by ? limit ?""",
            (timestamp, sort_key, limit)))

    def cards_due_for_final_review(self, grade, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=? and lapses>0 order by ? limit ?""",
            (grade, sort_key, limit)))

    def cards_new_memorising(self, grade, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=? and lapses=0 order by ? limit ?""",
            (grade, sort_key, limit)))
    
    def cards_unseen(self, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)      
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade=-1 order by ? limit ?""",
            (sort_key, limit)))
    
    def cards_learn_ahead(self, timestamp, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and grade>=2 and ?<next_rep order by ? limit ?""",
            (timestamp, sort_key, limit)))

    # Extra commands for custom schedulers.

    def set_scheduler_data(self, scheduler_data):
        self.con.execute("update cards set scheduler_data=?",
            (scheduler_data, ))

    def cards_with_scheduler_data(self, scheduler_data, sort_key="", limit=-1):
        sort_key = self._parse_sort_key(sort_key)
        return ((cursor[0], cursor[1]) for cursor in self.con.execute("""
            select _id, _fact_id from cards where
            active=1 and scheduler_data=? order by ? limit ?""",
            (scheduler_data, sort_key, limit)))

    def scheduler_data_count(self, scheduler_data):
        return self.con.execute("""select count() from cards
            where active=1 and scheduler_data=?""",
            (scheduler_data, )).fetchone()[0]        
