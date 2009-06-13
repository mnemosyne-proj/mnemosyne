#
# test_ui_controller_review.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestUIControllerReview(MnemosyneTest):
   
    def test_1(self):
        card_1 = None
        self.ui_controller_review().reset()
        for i in range(10):
            fact_data = {"q": "question" + str(i),
                         "a": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_by_id("1")
            else:
                card_type = self.card_type_by_id("2")            
            card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60 
                self.database().update_card(card)
        self.ui_controller_review().new_question()
        self.ui_controller_review().show_answer()        
        assert self.ui_controller_review().card == card_1
        assert self.ui_controller_review().get_counters() == (0, 1, 15)       
        self.ui_controller_review().grade_answer(0)
        assert self.ui_controller_review().get_counters() == (1, 0, 15)
        self.ui_controller_review().grade_answer(2)
        assert self.ui_controller_review().get_counters() == (0, 0, 15)        

    def test_2(self):
        card_1 = None
        self.ui_controller_review().reset()
        for i in range(10):
            fact_data = {"q": "question" + str(i),
                         "a": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_by_id("1")
            else:
                card_type = self.card_type_by_id("2")            
            card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60
                self.database().update_card(card)
        self.ui_controller_review().new_question()
        assert self.ui_controller_review().card == card_1
        self.ui_controller_review().reload_counters()        
        assert self.ui_controller_review().get_counters() == (0, 1, 15)       
        self.ui_controller_review().grade_answer(0)
        self.ui_controller_review().reload_counters()  
        assert self.ui_controller_review().get_counters() == (1, 0, 15)
        self.ui_controller_review().grade_answer(2)
        self.ui_controller_review().reload_counters()  
        assert self.ui_controller_review().get_counters() == (0, 0, 15)    
