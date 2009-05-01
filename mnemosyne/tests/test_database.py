#
# test_database.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.category import Category
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import database, plugins
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.exceptions import SaveError, LoadError
from mnemosyne.libmnemosyne.exceptions import MissingPluginError, PluginError


class TestDatabase(MnemosyneTest):

    def test_categories(self):
        cat = Category("test")
        database().add_category(cat)
        assert database().category_names() == [u"test"]
        cat.name = "test2"
        database().update_category(cat)
        assert database().category_names() == [u"test2"]        

    def test_new_cards(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        old_card = ui_controller_main().create_new_cards(fact_data, card_type,
                                 grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        old_fact = old_card.fact
        database().unload()

        database().load(config()["path"])
        assert database().fact_count() == 1
        card = database().get_card(old_card._id)
        fact = card.fact
        
        assert fact.data["q"] == "question"
        assert fact.data["a"] == "answer"
        assert fact.id == old_fact.id
        assert fact.creation_date == old_fact.creation_date
        assert fact.modification_date == old_fact.creation_date
        assert fact.needs_sync == old_fact.needs_sync        
        assert card.categories[0].name == old_card.categories[0].name

        assert card.fact == old_card.fact
        assert card.fact_view == old_card.fact_view       
        assert card.id == old_card.id
        assert card.grade == old_card.grade
        assert card.easiness == old_card.easiness
        assert card.acq_reps == old_card.acq_reps
        assert card.ret_reps == old_card.ret_reps
        assert card.lapses == old_card.lapses
        assert card.acq_reps_since_lapse == old_card.acq_reps_since_lapse
        assert card.last_rep == old_card.last_rep
        assert card.next_rep == old_card.next_rep
        assert card.unseen == old_card.unseen
        assert card.extra_data == old_card.extra_data
        assert card.scheduler_data == old_card.scheduler_data
        assert card.needs_sync == old_card.needs_sync
        assert card.active == old_card.active
        assert card.in_view == old_card.in_view
        
        # Modify cards

        card.grade = -1
        card.easiness = -2
        card.acq_reps = -3
        card.ret_reps = -4
        card.lapses = -5
        card.acq_reps_since_lapse = -6
        card.last_rep = -7
        card.next_rep = -8
        card.unseen = False
        card.extra_data = "extra"
        card.scheduler_data = 1
        card.needs_sync = True
        card.active = False
        card.in_view = False
        
        database().update_card(card)
        new_card = list(database().cards_from_fact(fact))[0]
        
        assert card.grade == -1
        assert card.easiness == -2
        assert card.acq_reps == -3
        assert card.ret_reps == -4
        assert card.lapses == -5
        assert card.acq_reps_since_lapse == -6
        assert card.last_rep == -7
        assert card.next_rep == -8
        assert card.unseen == False
        assert card.extra_data == "extra"
        assert card.scheduler_data == 1
        assert card.needs_sync == True
        assert card.active == False
        assert card.in_view == False
        
    def test_update_category(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        fact = card.fact
        ui_controller_main().update_related_cards(fact, fact_data, card_type,
            new_cat_names=["default1"], correspondence=[])
        new_card = database().get_card(card._id)
        assert new_card.categories[0].name == "default1"     
        
    @raises(LoadError)
    def test_load_unexisting_file(self):        
        database().load("unexisting")
        
    def test_clones(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_1")
        
        new_card_type = card_type_by_id("1_CLONED.my_1")
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        ui_controller_main().file_save()       
        database().unload()
        Mnemosyne().finalise()
        
        Mnemosyne().initialise(os.path.abspath("dot_test"))
        assert database().fact_count() == 1
        _card_id, _fact_id = list(database().cards_unseen(0))[0]
        fact = database().get_fact(_fact_id)
        card_type = card_type_by_id("1_CLONED.my_1")        
        assert fact.card_type.id == "1_CLONED.my_1"
        assert fact.card_type == card_type

    def test_plugin_and_clones(self):
        for plugin in plugins():
            if plugin.provides == "card_type" and plugin.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = card_type_by_id("4")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = card_type_by_id("4_CLONED.my_4")
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        ui_controller_main().file_save()       
        database().unload()
        Mnemosyne().finalise()
        
        Mnemosyne().initialise(os.path.abspath("dot_test"))
        assert database().fact_count() == 1
        _card_id, _fact_id = list(database().cards_unseen(0))[0]
        fact = database().get_fact(_fact_id)
        card_type = card_type_by_id("4")           
        card_type = card_type_by_id("4_CLONED.my_4")        
        assert fact.card_type.id == "4_CLONED.my_4"
        assert fact.card_type == card_type
        
        card = database().cards_from_fact(fact)[0]
        card.question()

    def test_new_database_overriding_existing_one(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        database().new(config()["path"])

        assert database().fact_count() == 0

    def test_delete_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()

        fact = card.fact
        database().delete_fact_and_related_data(fact)
        
        assert database().fact_count() == 0
        assert len(database().category_names()) == 0
        
    @raises(MissingPluginError)
    def test_missing_plugin(self):
        for plugin in plugins():
            if plugin.provides == "card_type" and plugin.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = card_type_by_id("4")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = card_type_by_id("4_CLONED.my_4")
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        ui_controller_main().file_save()       
        database().unload()
        Mnemosyne().finalise()
        
        Mnemosyne().initialise(os.path.abspath("dot_test"))
        database().unload()
        
        # Artificially remove plugin.
        for plugin in plugins():
            if plugin.provides == "card_type" and plugin.id == "4":
                plugin.deactivate()
                component_manager.unregister("plugin", plugin)
                break                    
        database().load(config()["path"])
        
    def infinity(self):
        return 1/0
        
    @raises(PluginError)
    def test_corrupt_plugin(self):
        for plugin in plugins():
            if plugin.provides == "card_type" and plugin.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = card_type_by_id("4")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = card_type_by_id("4_CLONED.my_4")
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        ui_controller_main().file_save()       
        database().unload()
        Mnemosyne().finalise()
        
        Mnemosyne().initialise(os.path.abspath("dot_test"))
        database().unload()
        
        # Artificially mutilate plugin.
        for plugin in plugins():
            if plugin.provides == "card_type" and plugin.id == "4":
                plugin.deactivate()
                plugin.activate = self.infinity
                break
                    
        database().load(config()["path"])

    def test_dont_overwrite_failed_load(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        database().unload()
        database().load_failed = True
        assert database().save(config()["path"]) == -1
        
    def test_save_as(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        new_name = config()["path"] + ".bak"
        assert database().save(config()["path"] + ".bak") != -1
        assert config()["path"] == new_name
        
    def test_has_fact_with_data(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        assert database().has_fact_with_data(fact_data, card_type) == True

        fact_data = {"q": "question2",
                     "a": "answer2"}
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"]) 
        assert database().has_fact_with_data(fact_data, card_type) == True
        
        fact_data = {"q": "question",
                     "a": "answer2"}        
        assert database().has_fact_with_data(fact_data, card_type) == False

    def test_duplicates_for_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        fact = card.fact

        fact_data = {"q": "question_",
                     "a": "answer_"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
            grade=0, cat_names=["default"], warn=False)
        assert len(database().duplicates_for_fact(fact)) == 0
        
        fact_data = {"q": "question1",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
            grade=0, cat_names=["default"], warn=False)
        assert len(database().duplicates_for_fact(fact)) == 0
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
            grade=0, cat_names=["default"], warn=False)
        assert len(database().duplicates_for_fact(fact)) == 1
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
            grade=0, cat_names=["default"], warn=False)
        assert len(database().duplicates_for_fact(fact)) == 1
        
    def test_card_types_in_use(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        assert len(database().card_types_in_use()) == 1
        
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])        
        assert len(database().card_types_in_use()) == 2

    @raises(LoadError)
    def test_format_mismatch(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        database().save()
        database().unload()
        database().version = "Wrong"
        database().load(config()["path"])

    def test_vacuum(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        for count in range(6):
            database().save()
            database().unload()
            database().load(config()["path"])
            
    def test_activate_cards(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type_1,
                                              grade=0, cat_names=["default"])
        assert database().active_count() == 1
        
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_2 = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=0, cat_names=["default"])
        assert database().active_count() == 3

        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default")])
        assert database().active_count() == 3

        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default")])
        assert database().active_count() == 2
        
        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default2")])
        assert database().active_count() == 0
        
        fact_data = {"q": "question2",
                     "a": "answer2"}
        ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=0, cat_names=["default2"])
        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default2")])        
        assert database().active_count() == 2

        fact_data = {"q": "question3",
                     "a": "answer3"}
        ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=0, cat_names=["default3",
                                                                  "default4"])
        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default3")])
        assert database().active_count() == 2

        database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [database().get_or_create_category_with_name("default3")])
        assert database().active_count() == 1

        database().set_cards_active([(card_type_1, card_type_1.fact_views[0])],
            [database().get_or_create_category_with_name("default3")])
        assert database().active_count() == 0        
        
