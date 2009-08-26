#
# test_scheduler.py <Peter.Bienstman@UGent.be>
#

import time
from mnemosyne_test import MnemosyneTest


class TestScheduler(MnemosyneTest):

    def test_1(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "3", "a": "a"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        fact_data = {"q": "4", "a": "a"}
        card_4 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        card_4.next_rep -= 1000 * 24 * 60 * 60
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
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.config()["grade_0_cards_in_hand"] = 0
        
        assert self.scheduler().get_next_card() is None
        
    def test_grade_0_limit(self):
        card_type = self.card_type_by_id("1")
        for i in range(10):
            fact_data = {"q": str(i), "a": "a"}
            self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]    
        self.config()["grade_0_cards_in_hand"] = 3
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
            self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True
        for i in range(30):
            card = self.scheduler().get_next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)
            
    def test_learn_ahead_2(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        old_card = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True      
        for i in range(3):
            card = self.scheduler().get_next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)
        fact_data = {"q": "2", "a": "a"}
        new_card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        assert self.scheduler().get_next_card() == new_card


    def test_4(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        card = self.scheduler().get_next_card()
        self.scheduler().grade_answer(card, 0)
        card = self.scheduler().get_next_card()
        self.scheduler().grade_answer(card, 0)        
        self.database().update_card(card)

        assert self.scheduler().get_next_card() != None
        
    def test_5(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(0)

        assert self.review_controller().card != None
        
    def test_6(self):
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"q": "question" + str(i),
                         "a": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_by_id("1")
            else:
                card_type = self.card_type_by_id("2")            
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            card.next_rep = time.time() - 24 * 60 * 60
            card.last_rep = card.next_rep - i * 24 * 60 * 60
            self.database().update_card(card)
            if i == 0:
                card_1 = card
        self.review_controller().new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(0)
        card_1_new = self.database().get_card(card_1._id, id_is_internal=True)
        assert card_1_new.grade == 0

    def test_learn_ahead_3(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()
        self.review_controller().grade_answer(5)    
        self.review_controller().learning_ahead = True
        for i in range(10):
            self.review_controller().new_question()
            assert self.review_controller().card is not None
            self.review_controller().grade_answer(2)

    def test_learn_ahead_4(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True
        self.review_controller().new_question()
        self.review_controller().grade_answer(0)
        assert self.review_controller().scheduled_count == 0
                    
    def test_learn_related_together(self):
        self.config()["memorise_related_cards_on_same_day"] = True
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        for i in range(7):
            fact_data = {"q": str(i), "a": "a"}
            self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(5)
        cards = set()
        for i in range(30):
            self.review_controller().grade_answer(1)
            cards.add(self.review_controller().card._id)
        assert card_2._id in cards
        
    def test_learn_related_together_2(self):
        self.config()["memorise_related_cards_on_same_day"] = False
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        for i in range(7):
            fact_data = {"q": str(i), "a": "a"}
            self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(5)
        cards = set()
        for i in range(30):
            self.review_controller().grade_answer(1)
            cards.add(self.review_controller().card._id)
        assert card_2._id not in cards

    def test_learn_related_together_3(self):
        # Relax requirements if there are not enough cards.
        self.config()["memorise_related_cards_on_same_day"] = False
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(5)
        cards = set()
        for i in range(30):
            self.review_controller().grade_answer(1)
            cards.add(self.review_controller().card._id)
        assert card_2._id in cards

    def test_order(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        card_1.next_rep = time.time() - 24 * 60 * 60
        card_1.last_rep = card_1.next_rep - 2 * 24 * 60 * 60
        self.database().update_card(card_1)
        fact_data = {"q": "2", "a": "a"}        
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        card_2.next_rep = time.time() - 24 * 60 * 60
        card_2.last_rep = card_2.next_rep - 24 * 60 * 60
        self.database().update_card(card_2)

        # Shortest interval should go first
        assert self.scheduler().get_next_card() == card_2
