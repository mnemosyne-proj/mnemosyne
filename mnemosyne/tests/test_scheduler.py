#
# test_scheduler.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestScheduler(MnemosyneTest):

    def test_1(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=1, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "3", "a": "a"}
        card_3 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=2, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "4", "a": "a"}
        card_4 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=2, cat_names=["default"], warn=False)[0]
        card_4.next_rep -= 1000
        self.database().update_card(card_4)

        # Due cards.
        assert self.scheduler().get_next_card() == card_4
        self.scheduler().grade_answer(card_4, 0)
        self.database().update_card(card_4)
    
        # Failed scheduled cards.
        assert self.scheduler().get_next_card() == card_4
        self.scheduler().grade_answer(card_4, 2)
        self.database().update_card(card_4)
        
        # Unseen cards.
        card = self.scheduler().get_next_card()
        assert card == card_1 or card == card_2
        self.scheduler().grade_answer(card, 0)
        self.database().update_card(card)
            
        # Cards currently being memorised.
        card = self.scheduler().get_next_card()
        assert card == card_1 or card == card_2
        self.scheduler().grade_answer(card, 1)
        self.database().update_card(card)
        
        card = self.scheduler().get_next_card()
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards = [card]
        
        card = self.scheduler().get_next_card()
        assert card not in learned_cards
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards.append(card)
        
        assert self.scheduler().get_next_card() == None

        # Learn ahead.
        
        assert self.scheduler().get_next_card(learn_ahead=True) != None


    def test_2(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=1, cat_names=["default"], warn=False)[0]
        self.config()["grade_0_items_at_once"] = 0
        
        assert self.scheduler().get_next_card() == card_2
        
    def test_3(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        self.config()["grade_0_items_at_once"] = 0
        
        assert self.scheduler().get_next_card() == None
        
    def test_grade_0_limit(self):
        card_type = self.card_type_by_id("1")
        for i in range(10):
            fact_data = {"q": str(i), "a": "a"}
            self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]    
        self.config()["grade_0_items_at_once"] = 3
        cards = set()
        for i in range(10):
            card = self.scheduler().get_next_card()
            self.scheduler().grade_answer(card, 0)
            self.database().update_card(card)
            cards.add(card._id)
        assert len(cards) == 3

    def test_learn_ahead(self):
        card_type = self.card_type_by_id("1")
        for i in range(5):
            fact_data = {"q": str(i), "a": "a"}
            self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=5, cat_names=["default"], warn=False)[0]
        self.ui_controller_review().learning_ahead = True
        for i in range(30):
            card = self.scheduler().get_next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)
            
    def test_learn_ahead_2(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        old_card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=5, cat_names=["default"], warn=False)[0]
        self.ui_controller_review().learning_ahead = True      
        for i in range(3):
            card = self.scheduler().get_next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)
        fact_data = {"q": "2", "a": "a"}
        new_card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        assert self.scheduler().get_next_card() == new_card


    def test_4(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]

        card = self.scheduler().get_next_card()
        self.scheduler().grade_answer(card, 0)
        card = self.scheduler().get_next_card()
        self.scheduler().grade_answer(card, 0)        
        self.database().update_card(card)

        assert self.scheduler().get_next_card() != None
        
    def test_5(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]

        self.ui_controller_review().new_question()
        self.ui_controller_review().grade_answer(0)
        self.ui_controller_review().grade_answer(0)

        assert self.ui_controller_review().card != None
        
    def test_6(self):
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
                    grade=4, cat_names=["default" + str(i)])[0]
            card.next_rep -= 1000-i
            self.database().update_card(card)
            if i == 0:
                card_1 = card
        self.ui_controller_review().new_question()
        assert self.ui_controller_review().card == card_1
        self.ui_controller_review().grade_answer(0)
        card_1_new = self.database().get_card(card_1._id)
        assert card_1_new.grade == 0
