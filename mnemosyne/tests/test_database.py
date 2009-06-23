#
# test_database.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import expand_path


class TestDatabase(MnemosyneTest):

    def test_tags(self):
        cat = Tag("test")
        self.database().add_tag(cat)
        assert self.database().tag_names() == [u"test"]
        cat.name = "test2"
        self.database().update_tag(cat)
        assert self.database().tag_names() == [u"test2"]        

    def test_new_cards(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        old_card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        old_fact = old_card.fact
        self.database().unload()

        self.database().load(self.config()["path"])
        assert self.database().fact_count() == 1
        card = self.database().get_card(old_card._id)
        fact = card.fact
        
        assert fact.data["q"] == "question"
        assert fact.data["a"] == "answer"
        assert fact.id == old_fact.id
        assert fact.creation_time == old_fact.creation_time
        assert fact.modification_time == old_fact.modification_time     
        assert [tag.name for tag in card.tags] == \
               [tag.name for tag in old_card.tags]

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
        assert card.extra_data == old_card.extra_data
        assert card.scheduler_data == old_card.scheduler_data
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
        card.extra_data = "extra"
        card.scheduler_data = 1
        card.active = False
        card.in_view = False
        
        self.database().update_card(card)
        new_card = list(self.database().cards_from_fact(fact))[0]
        
        assert card.grade == -1
        assert card.easiness == -2
        assert card.acq_reps == -3
        assert card.ret_reps == -4
        assert card.lapses == -5
        assert card.acq_reps_since_lapse == -6
        assert card.last_rep == -7
        assert card.next_rep == -8
        assert card.extra_data == "extra"
        assert card.scheduler_data == 1
        assert card.active == False
        assert card.in_view == False
        
    def test_update_tag(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        fact = card.fact
        self.ui_controller_main().update_related_cards(fact, fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
        new_card = self.database().get_card(card._id)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "default1" in tag_names
        
    def test_clones(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_1")
        
        new_card_type = self.card_type_by_id("1_CLONED.my_1")
        self.ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        self.ui_controller_main().file_save()       

        self.mnemosyne.finalise()
        self.restart()
        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen(0))[0]
        fact = self.database().get_fact(_fact_id)
        card_type = self.card_type_by_id("1_CLONED.my_1")        
        assert fact.card_type.id == "1_CLONED.my_1"
        assert fact.card_type == card_type

    def test_plugin_and_clones(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_by_id("4")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        assert self.database().fact_count() == 1
        
        self.ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = self.card_type_by_id("4_CLONED.my_4")
        self.ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        assert self.database().fact_count() == 1        
        self.ui_controller_main().file_save()

        self.mnemosyne.finalise()

        self.restart()
        
        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen(0))[0]
        fact = self.database().get_fact(_fact_id)
        card_type = self.card_type_by_id("4")           
        card_type = self.card_type_by_id("4_CLONED.my_4")        
        assert fact.card_type.id == "4_CLONED.my_4"
        assert fact.card_type == card_type
        
        card = self.database().cards_from_fact(fact)[0]
        card.question()

    def test_new_database_overriding_existing_one(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()

        self.database().new(self.config()["path"])

        assert self.database().fact_count() == 0

    def test_delete_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        self.database().delete_fact_and_related_data(fact)
        
        assert self.database().fact_count() == 0
        assert len(self.database().tag_names()) == 0
        
    @raises(RuntimeError)
    def test_missing_plugin(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_by_id("4")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = self.card_type_by_id("4_CLONED.my_4")
        self.ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        self.ui_controller_main().file_save()

        self.mnemosyne.finalise()
        self.restart()
        self.database().unload()

        # Artificially remove plugin.
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.deactivate()
                self.mnemosyne.component_manager.unregister(plugin)
        self.database().load(self.config()["path"])
        
    def infinity(self):
        return 1/0
        
    @raises(RuntimeError)
    def test_corrupt_plugin(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_by_id("4")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        fact = card.fact
        fact.card_type.clone("my_4")
        
        new_card_type = self.card_type_by_id("4_CLONED.my_4")
        self.ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        self.ui_controller_main().file_save()       

        self.mnemosyne.finalise()
        self.restart()
        self.database().unload()
        
        # Artificially mutilate plugin.
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.deactivate()
                plugin.activate = self.infinity
                break
                    
        self.database().load(self.config()["path"])

    def test_dont_overwrite_failed_load(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        
        self.database().load_failed = True
        assert self.database().save(self.config()["path"]) == -1
        
    def test_save_as(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        new_name = self.config()["path"] + ".bak"
        assert self.database().save(self.config()["path"] + ".bak") != -1
        assert self.config()["path"] == new_name
        assert new_name != expand_path(new_name, self.config().basedir)
        
    def test_has_fact_with_data(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert self.database().has_fact_with_data(fact_data, card_type) == True

        fact_data = {"q": "question2",
                     "a": "answer2"}
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"]) 
        assert self.database().has_fact_with_data(fact_data, card_type) == True
        
        fact_data = {"q": "question",
                     "a": "answer2"}        
        assert self.database().has_fact_with_data(fact_data, card_type) == False

    def test_duplicates_for_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact

        fact_data = {"q": "question_",
                     "a": "answer_"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], warn=False)
        assert len(self.database().duplicates_for_fact(fact)) == 0
        
        fact_data = {"q": "question1",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], warn=False)
        assert len(self.database().duplicates_for_fact(fact)) == 0
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], warn=False)
        assert len(self.database().duplicates_for_fact(fact)) == 1
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = self.card_type_by_id("2")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], warn=False)
        assert len(self.database().duplicates_for_fact(fact)) == 1
        
    def test_card_types_in_use(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert len(self.database().card_types_in_use()) == 1
        
        card_type = self.card_type_by_id("2")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])        
        assert len(self.database().card_types_in_use()) == 2

    @raises(RuntimeError)
    def test_format_mismatch(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.database().save()
        self.database().unload()
        self.database().version = "Wrong"
        self.database().load(self.config()["path"])

    def test_vacuum(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        for count in range(6):
            self.database().save()
            self.database().unload()
            self.database().load(self.config()["path"])
            
    def test_activate_cards(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type_1,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1
        
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_2 = self.card_type_by_id("2")
        self.ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 3

        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default")])
        assert self.database().active_count() == 3

        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default")])
        assert self.database().active_count() == 2
        
        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default2")])
        assert self.database().active_count() == 0
        
        fact_data = {"q": "question2",
                     "a": "answer2"}
        self.ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default2"])
        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default2")])        
        assert self.database().active_count() == 2

        fact_data = {"q": "question3",
                     "a": "answer3"}
        self.ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default3",
                                                                  "default4"])
        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default3")])
        assert self.database().active_count() == 2

        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0]),
                                   (card_type_2, card_type_2.fact_views[1])],
            [self.database().get_or_create_tag_with_name("default3")])
        assert self.database().active_count() == 1

        self.database().set_cards_active([(card_type_1, card_type_1.fact_views[0])],
            [self.database().get_or_create_tag_with_name("default3")])
        assert self.database().active_count() == 0        
        
    def test_schedule_on_same_day(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_2 = self.card_type_by_id("2")
        card_1, card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_3, card_4 = self.ui_controller_main().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])        
        self.ui_controller_review().new_question()
        assert card_1 == self.ui_controller_review().card
        assert self.database().count_related_cards_with_next_rep(card_1, 0) == 0
        self.ui_controller_review().grade_answer(2)
        card_1 = self.database().get_card(card_1._id)
        card_3.next_rep = card_1.next_rep
        card_3.grade = 2
        self.database().update_card(card_3)
        assert self.database().count_related_cards_with_next_rep(card_2, card_1.next_rep) == 1        
        assert self.database().count_related_cards_with_next_rep(card_3, card_1.next_rep) == 0
        assert self.database().count_related_cards_with_next_rep(card_1, card_1.next_rep) == 0       
