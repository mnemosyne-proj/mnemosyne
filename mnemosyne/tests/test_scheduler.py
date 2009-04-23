#
# test_scheduler.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main


class TestScheduler:

    def setup(self):
        os.system("rm -fr dot_test")
        initialise(os.path.abspath("dot_test"))        

    def test_1(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=1, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "3", "a": "a"}
        card_3 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=2, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "4", "a": "a"}
        card_4 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=2, cat_names=["default"], warn=False)[0]
        card_4.next_rep -= 1000
        database().update_card(card_4)

        # Due cards.
        assert scheduler().get_next_card() == card_4
        scheduler().process_answer(card_4, 0)
    
        # Failed scheduled cards.
        assert scheduler().get_next_card() == card_4
        scheduler().process_answer(card_4, 2)

        # Unseen cards.
        card = scheduler().get_next_card()
        assert card == card_1 or card == card_2
        scheduler().process_answer(card, 0)

        # Cards currently being memorised.
        card = scheduler().get_next_card()
        assert card == card_1 or card == card_2
        scheduler().process_answer(card, 1)

        card = scheduler().get_next_card()
        scheduler().process_answer(card, 2)
        learned_cards = [card]
        
        card = scheduler().get_next_card()
        assert card not in learned_cards
        scheduler().process_answer(card, 2)
        learned_cards.append(card)
        
        assert scheduler().get_next_card() == None

        # Learn ahead.
        
        assert scheduler().get_next_card(learn_ahead=True) != None


    def test_2(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=1, cat_names=["default"], warn=False)[0]
        config()["grade_0_items_at_once"] = 0
        
        assert scheduler().get_next_card() == card_2
        
    def test_3(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        fact_data = {"q": "2", "a": "a"}        
        card_2 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        config()["grade_0_items_at_once"] = 0
        
        assert scheduler().get_next_card() == None
        
    def test_grade_0_limit(self):
        card_type = card_type_by_id("1")
        for i in range(20):
            fact_data = {"q": str(i), "a": "a"}
            ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]    
        config()["grade_0_items_at_once"] = 3
        cards = set()
        for i in range(10):
            card = scheduler().get_next_card()
            scheduler().process_answer(card, 0)
            cards.add(card.id)
        print cards
        assert len(cards) == 3
        
    def teardown(self):
        finalise()
