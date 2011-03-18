#
# test_review_controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest

from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class TestReviewController(MnemosyneTest):
   
    def test_1(self):
        self.review_controller().heartbeat()
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"f": "question" + str(i),
                         "b": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_by_id("1")
            else:
                card_type = self.card_type_by_id("2")            
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60 
                self.database().update_card(card)
        self.review_controller().set_render_chain("default")
        self.review_controller().show_new_question()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().show_answer()        
        assert self.review_controller().card == card_1
        assert self.review_controller().counters() == (1, 0, 15)       
        self.review_controller().grade_answer(0)
        assert self.review_controller().counters() == (0, 1, 15)
        self.review_controller().grade_answer(2)
        assert self.review_controller().counters() == (0, 0, 15)
        self.review_controller().next_rep_string(0)
        self.review_controller().next_rep_string(1)
        self.review_controller().next_rep_string(2)

    def test_2(self):
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"f": "question" + str(i),
                         "b": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_by_id("1")
            else:
                card_type = self.card_type_by_id("2")            
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60
                self.database().update_card(card)
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.review_controller().reload_counters()        
        assert self.review_controller().counters() == (1, 0, 15)       
        self.review_controller().grade_answer(0)
        self.review_controller().reload_counters()  
        assert self.review_controller().counters() == (0, 1, 15)
        self.review_controller().grade_answer(2)
        self.review_controller().reload_counters()  
        assert self.review_controller().counters() == (0, 0, 15)

        self.mnemosyne.review_widget().set_grade_enabled(1, True)

    def test_reset_but_try_to_keep_current_card_turned_inactive(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["forbidden"])[0]     
        self.review_controller().show_new_question()
        assert self.review_controller().card == card
        
        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c.active_tag__ids = set([self.database().get_or_create_tag_with_name("active")._id])
        c.forbidden_tag__ids = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0
        
        assert self.review_controller().card == card
        self.review_controller().reset_but_try_to_keep_current_card()
        assert self.review_controller().card is None 