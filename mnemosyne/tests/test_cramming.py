#
# test_cramming.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review


class TestScheduler(MnemosyneTest):

    def setup(self):

        os.system("rm -fr dot_test")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.initialise(os.path.abspath("dot_test"),
             extra_components=[("scheduler", "Cramming",
             "mnemosyne.libmnemosyne.schedulers.cramming")])

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

        # Fail the cards a couple of times.

        for i in range(8):
            card = scheduler().get_next_card()
            scheduler().grade_answer(card, 0)

        # Pass the cards a couple of times.

        for i in range(8):
            card = scheduler().get_next_card()
            scheduler().grade_answer(card, 5)
 
