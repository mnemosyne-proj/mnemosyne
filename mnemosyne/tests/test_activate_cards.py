#
# test_activate_cards.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion

class TestActivateCards(MnemosyneTest):
    
    def test_activate_cards_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1
        
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_2 = self.card_type_by_id("2")
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 3
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("default")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        assert self.database().active_count() == 3

        c.deactivated_card_type_fact_views = \
            set([(card_type_2, card_type_2.fact_views[0])])
        c.required_tags = set([self.database().get_or_create_tag_with_name("default")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)    
        assert self.database().active_count() == 2

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("default2")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        assert self.database().active_count() == 0
        
        fact_data = {"q": "question2",
                     "a": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default2"])
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("default2")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)    
        assert self.database().active_count() == 2

        fact_data = {"q": "question3",
                     "a": "answer3"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default3",
                                                                  "default4"])
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("default3")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c) 
        assert self.database().active_count() == 2

        c.deactivated_card_type_fact_views = \
            set([(card_type_2, card_type_2.fact_views[0])])
        c.required_tags = set([self.database().get_or_create_tag_with_name("default3")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c) 
        assert self.database().active_count() == 1

        c.deactivated_card_type_fact_views = \
            set([(card_type_2, card_type_2.fact_views[0]),
                 (card_type_2, card_type_2.fact_views[1])])
        c.required_tags = set([self.database().get_or_create_tag_with_name("default3")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        assert self.database().active_count() == 0
        
    def test_activate_cards_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = self.card_type_by_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["required", "forbidden"])
        assert self.database().active_count() == 1
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("required")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("required")])
        c.forbidden_tags = set([self.database().get_or_create_tag_with_name("forbidden")])
        self.database().set_current_activity_criterion(c)
        assert self.database().active_count() == 0

    def test_activate_cards_3(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag1"])[0]
        self.review_controller().new_question()
        
        assert self.review_controller().card == card
        assert self.review_controller().get_counters() == (0, 1, 1)
        
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_type_2 = self.card_type_by_id("1")
        cards = self.controller().create_new_cards(fact_data, card_type_2,
           grade=-1, tag_names=["tag2"])
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("tag2")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        
        assert self.review_controller().card != card
        assert self.review_controller().get_counters() == (0, 2, 2)
        
    def test_activate_cards_4(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type_1 = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag"])[0]
        self.review_controller().new_question()
        
        assert self.review_controller().card == card
        assert self.review_controller().get_counters() == (0, 1, 1)
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("tag2")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        assert self.review_controller().card is None       
        assert self.review_controller().get_counters() == (0, 0, 0)

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_views = set()
        c.required_tags = set([self.database().get_or_create_tag_with_name("tag")])
        c.forbidden_tags = set()
        self.database().set_current_activity_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        
        assert self.review_controller().card == card
        assert self.review_controller().get_counters() == (0, 1, 1)
