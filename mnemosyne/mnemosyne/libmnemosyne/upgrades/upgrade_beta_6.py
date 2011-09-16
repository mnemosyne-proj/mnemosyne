#
# upgrade_beta_6.py <Peter.Bienstman@UGent.be>
#

import sqlite3

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import numeric_string_cmp, mangle
from mnemosyne.libmnemosyne.utils import expand_path, contract_path


class UpgradeBeta6(Component):

    def load_old(self, path):
        if self.database().is_loaded():
            self.database().unload()
        self.database()._path = expand_path(path, self.config().data_dir)
        # Check database version.
        try:
            sql_res = self.database().con.execute("""select value from global_variables
                where key=?""", ("version", )).fetchone()
        except sqlite3.OperationalError:
            self.database().main_widget().show_error(
                _("Another copy of Mnemosyne is still running.") + "\n" + \
                _("Continuing is impossible and will lead to data loss!"))
            sys.exit()
        except:
            raise RuntimeError, _("Unable to load file.") + traceback_string()
        if sql_res is None:
            raise RuntimeError, _("Unable to load file, query failed")
        if sql_res["value"] != self.database().version:
            raise RuntimeError, \
                _("Unable to load file: database version mismatch.")
        # Identify missing plugins for card types and their parents.
        plugin_needed = set()
        active_ids = set(card_type.id for card_type in self.database().card_types())
        # Sometimes corruption keeps the global_variables table intact,
        # but not the cards table...
        try:
            result = self.database().con.execute("""select distinct card_type_id
                from cards""")
        except:
            raise RuntimeError, _("Unable to load file.") + traceback_string()        
        for cursor in result:
            id = cursor[0]
            while "::" in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit("::", 1)
                if id not in active_ids:
                    plugin_needed.add(id)
            if id not in active_ids:
                plugin_needed.add(id)
        for card_type_id in plugin_needed:
            try:
                self.database()._activate_plugin_for_card_type(card_type_id)
            except RuntimeError, exception:
                self.database()._connection.close()
                self.database()._connection = None
                raise exception

    def fact_view_old(self, id, is_id_internal):
        # Since there are so few of them, we don't use internal _ids.
        # ids should be unique too.
        sql_res = self.database().con.execute("select * from fact_views where id=?",
                 (id, )).fetchone()          
        fact_view = FactView(sql_res["name"], sql_res["id"])
        fact_view.q_fact_keys = eval(sql_res["q_fields"])
        fact_view.a_fact_keys = eval(sql_res["a_fields"])
        fact_view.q_fact_key_decorators= eval(sql_res["q_field_decorators"])
        fact_view.a_fact_key_decorators = eval(sql_res["a_field_decorators"])
        for attr in ["a_on_top_of_q", "type_answer"]:
            setattr(fact_view, attr, bool(sql_res[attr]))
        self.database()._construct_extra_data(sql_res, fact_view)
        return fact_view

    def card_type_old(self, id, is_id_internal):
        # Since there are so few of them, we don't use internal _ids.
        # ids should be unique too.
        if id in self.database().component_manager.card_type_with_id:
            return self.database().component_manager.card_type_with_id[id]
        parent_id, child_id = "", id
        if "::" in id:
            parent_id, child_id = id.rsplit("::", 1)
            parent = self.card_type_old(parent_id, is_id_internal=-1)
        else:
            parent = CardType(self.database().component_manager)
        sql_res = self.database().con.execute("select * from card_types where id=?",
                                   (id, )).fetchone()
        card_type = type(mangle(id), (parent.__class__, ),
            {"name": sql_res["name"], "id": id})(self.database().component_manager)

        card_type.fact_keys_and_names = eval(sql_res["fields"])
        card_type.unique_fact_keys = eval(sql_res["unique_fields"])
        card_type.required_fact_keys = eval(sql_res["required_fields"])
        card_type.keyboard_shortcuts = eval(sql_res["keyboard_shortcuts"])
        self.database()._construct_extra_data(sql_res, card_type)
        card_type.fact_views = [self.fact_view_old(fact_view_id,
            is_id_internal=False) for fact_view_id in \
            eval(sql_res["fact_view_ids"])]
        return card_type
            
    def run(self, filename):
        if not filename:
            filename = self.config()["path"]
        filename = expand_path(filename, self.config().data_dir)
        self.load_old(filename)
        # See if we need to upgrade.
        con = self.database().con
        upgrade_needed = False
        try:
            con.execute("select q_fact_keys from fact_views")
        except sqlite3.OperationalError:
            upgrade_needed = True
        if not upgrade_needed:
            self.database()._connection.close()
            self.database()._connection = None
            self.database()._path = None  
            return
        # Upgrade.
        self.database().backup()
        fact_views = [self.fact_view_old(result[0], is_id_internal=False) \
            for result in con.execute("select id from fact_views")]
        card_types = [self.card_type_old(result[0], is_id_internal=False) \
            for result in con.execute("select id from card_types")]        
        con.executescript("""
            drop table fact_views;
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
            
            drop table card_types;
            create table card_types(
                id text primary key,
                name text,
                fact_keys_and_names text,
                unique_fact_keys text,
                required_fact_keys text,
                fact_view_ids text,
                keyboard_shortcuts text,
                extra_data text default ""
            );""")

        for fact_view in fact_views:
            self.database().add_fact_view(fact_view)
        for card_type in card_types:
            self.database().add_card_type(card_type)
            self.component_manager.register(card_type)
        con.commit()

