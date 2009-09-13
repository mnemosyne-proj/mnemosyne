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
        
