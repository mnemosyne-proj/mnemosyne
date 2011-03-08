#
# test_database.py <Peter.Bienstman@UGent.be>
#

import os

from nose.tools import raises

from openSM2sync.log_entry import EventTypes

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import expand_path


class TestDatabase(MnemosyneTest):

    def test_release(self):
        self.database().release_connection()
        self.database().release_connection()
        self.database().display_name()
        self.database().abandon()
        self.database().new("default.mem")

    def test_tags(self):
        tag = Tag("test")
        self.database().add_tag(tag)
        assert len(self.database().tags()) == 1
        assert self.database().tags()[0].name == u"test"
        tag.name = "test2"
        self.database().update_tag(tag)
        assert len(self.database().tags()) == 1
        assert self.database().tags()[0].name == u"test2"      

    def test_new_cards(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        old_card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["default"])[0]
        old_fact = old_card.fact
        self.database().unload()

        self.database().load(self.config()["path"])
        assert self.database().fact_count() == 1
        card = self.database().card(old_card._id, id_is_internal=True)
        fact = card.fact
        
        assert fact.data["q"] == "question"
        assert fact.data["a"] == "answer"
        assert fact.id == old_fact.id   
        assert [tag.name for tag in card.tags] == \
               [tag.name for tag in old_card.tags]

        assert card.fact == old_card.fact
        assert card.fact_view == old_card.fact_view       
        assert card.id == old_card.id
        assert card.creation_time == old_card.creation_time
        assert card.modification_time == old_card.modification_time  
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
        
    def test_update_tag(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, card_type,
            new_tag_names=["default1"], correspondence=[])
        new_card = self.database().card(card._id, id_is_internal=True)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "default1" in tag_names
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1
        
    def test_clones(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_1")
        
        new_card_type = self.card_type_by_id("1::my_1")
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               new_card_type, new_tag_names=["default2"], correspondence=[])
        self.mnemosyne.finalise()
        self.restart()
        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen())[0]
        fact = self.database().fact(_fact_id, id_is_internal=True)
        card_type = self.card_type_by_id("1::my_1")        
        assert card_type.id == "1::my_1"
        assert card_type == card_type

    def test_plugin_and_clones(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
        
        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_by_id("4")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        assert self.database().fact_count() == 1
        
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")
        
        new_card_type = self.card_type_by_id("4::my_4")
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               new_card_type, new_tag_names=["default2"], correspondence=[])
        assert self.database().fact_count() == 1        

        self.mnemosyne.finalise()

        self.restart()
        
        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen())[0]
        fact = self.database().fact(_fact_id, id_is_internal=True)
        card_type = self.card_type_by_id("4")           
        card_type = self.card_type_by_id("4::my_4")        
        assert card_type.id == "4::my_4"
        assert card_type == card_type
        
        card = self.database().cards_from_fact(fact)[0]
        card.question()

    def test_new_database_overriding_existing_one(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])

        self.database().new(self.config()["path"])

        assert self.database().fact_count() == 0

    def test_delete_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        self.controller().delete_facts_and_their_cards([fact])
        
        assert self.database().fact_count() == 0
        assert self.database().card_count() == 0
        assert len(self.database().tags()) == 0
        
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")
        
        new_card_type = self.card_type_by_id("4::my_4")
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               new_card_type, new_tag_names=["default2"], correspondence=[])

        self.mnemosyne.finalise()
        self.restart()

        # Artificially remove plugin.
        self.database().unload()
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")
        
        new_card_type = self.card_type_by_id("4::my_4")
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               new_card_type, new_tag_names=["default2"], correspondence=[])
        

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
        
    def test_save_as(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        new_name = self.config()["path"] + ".bak"
        assert self.database().save(self.config()["path"] + ".bak") != -1
        assert self.config()["path"] == new_name
        assert new_name != expand_path(new_name, self.config().data_dir)

    def test_duplicates_for_fact(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)[0]
        fact = card.fact

        fact_data = {"q": "question_",
                     "a": "answer_"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 0
        
        fact_data = {"q": "question1",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 0
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 1
        
        fact_data = {"q": "question",
                     "a": "answer1"}
        card_type = self.card_type_by_id("2")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 1
        
    def test_card_types_in_use(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert len(self.database().card_types_in_use()) == 1
        
        card_type = self.card_type_by_id("2")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])        
        assert len(self.database().card_types_in_use()) == 2

    @raises(RuntimeError)
    def test_format_mismatch(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.database().unload()
        self.database().version = "Wrong"
        self.database().load(self.config()["path"])

    def test_vacuum(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        for count in range(6):
            self.database().save()
            self.database().unload()
            self.database().load(self.config()["path"])
                    
    def test_schedule_on_same_day(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_2 = self.card_type_by_id("2")
        card_1, card_2 = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_3, card_4 = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])        
        self.review_controller().new_question()
        assert card_1 == self.review_controller().card
        assert self.database().count_sister_cards_with_next_rep(card_1, 0) == 0
        self.review_controller().grade_answer(2)
        card_1 = self.database().card(card_1._id, id_is_internal=True)
        card_3.next_rep = card_1.next_rep
        card_3.grade = 2
        self.database().update_card(card_3)
        assert self.database().count_sister_cards_with_next_rep(card_2, card_1.next_rep) == 1        
        assert self.database().count_sister_cards_with_next_rep(card_3, card_1.next_rep) == 0
        assert self.database().count_sister_cards_with_next_rep(card_1, card_1.next_rep) == 0

    def test_purge_backups(self):
        backup_dir = os.path.join(self.config().data_dir, "backups")
        for count in range(10):
            f = file(os.path.join(backup_dir, "default-%d.db" % count), "w")
        self.mnemosyne.finalise()
        backups = [f for f in os.listdir(backup_dir)]
        assert len(backups) == 5
        assert "default-0.db" not in backups
        self.restart()
