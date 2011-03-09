#
# test_activate_cards.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises
from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

class TestActivateCards(MnemosyneTest):
    
    def test_activate_cards_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1
        
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_2 = self.card_type_by_id("2")
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 3
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 3

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id)])
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)    
        assert self.database().active_count() == 2

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default2")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default2"])
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default2")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)    
        assert self.database().active_count() == 2

        fact_data = {"f": "question3",
                     "b": "answer3"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default3",
                                                                  "default4"])
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default3")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c) 
        assert self.database().active_count() == 2

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id)])
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default3")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c) 
        assert self.database().active_count() == 1

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id),
                 (card_type_2.id, card_type_2.fact_views[1].id)])
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("default3")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
    def test_activate_cards_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["active", "forbidden"])
        assert self.database().active_count() == 1
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("active")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("active")._id])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

    def test_activate_cards_3(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag1"])[0]
        self.review_controller().new_question()
        
        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_2 = self.card_type_by_id("2")
        cards = self.controller().create_new_cards(fact_data, card_type_2,
           grade=-1, tag_names=["tag2"])
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("tag2")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()
        
        assert self.review_controller().card != card
        assert self.review_controller().counters() == (0, 2, 2)
        
    def test_activate_cards_4(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag"])[0]
        self.review_controller().new_question()
        
        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("tag2")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()
                
        assert self.review_controller().card is None       
        assert self.review_controller().counters() == (0, 0, 0)

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("tag")._id])
        c.forbidden_tags__ids = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()
        
        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)

    def test_activate_cards_new(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])
        assert self.database().active_count() == 0
        
    def test_activate_cards_new_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c.active_tag__ids = set()
        c.forbidden_tag__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])
        assert self.database().active_count() == 0

    def test_activate_cards_edit(self):
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card_type_1 = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
        card_type_2 = self.card_type_by_id("2")
        self.controller().edit_sister_cards(card.fact, card.fact.data, card.card_type, 
               card_type_2, new_tag_names=["allowed"], correspondence=[])
        assert self.database().active_count() == 2

        c = list(self.database().criteria())[0]
        assert len(c.forbidden_tag__ids) == 0
        assert len(c.active_tag__ids) == 1

    def test_card_type(self):
        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break
        
        fact_data = {"text": "[foo]"}
        card_type_1 = self.card_type_by_id("5")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c.active_tag__ids = set()
        c.forbidden_tag__ids = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        self.controller().delete_facts_and_their_cards([card.fact])
        plugin.deactivate()
        c = self.database().current_criterion()
        assert len(c.deactivated_card_type_fact_view_ids) == 0
        
    def test_cached_scheduler_count(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag"])
        assert self.database().active_count() == 1
        self.review_controller().new_question()
        assert self.review_controller().active_count == 1        

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set()
        c.forbidden_tag__ids = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        assert self.database().active_count() == 0
        assert self.review_controller().active_count == 0

    def test_activate_cards_5(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["b"])
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["a"])
        assert self.database().active_count() == 2
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("a")._id,
                                 self.database().get_or_create_tag_with_name("b")._id])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("b")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

    @raises(AssertionError)
    def test_activate_cards_6(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["a"])
        
        fact_data = {"f": "question2",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["b"])
        assert self.database().active_count() == 2
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("b")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1
