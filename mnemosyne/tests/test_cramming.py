#
# test_cramming.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
from mnemosyne.libmnemosyne.plugins.cramming_plugin import CrammingPlugin
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.component_manager import config, plugins
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review


class Widget(MainWidget):

    def error_box(self, s1):
        raise NotImplementedError


class TestScheduler(MnemosyneTest):

    def setup(self):

        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_cramming", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))
        MnemosyneTest.setup(self)
        for plugin in plugins():
            if isinstance(plugin, CrammingPlugin):
                plugin.activate()
                break

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

        assert database().scheduler_data_count(Cramming.UNSEEN) == 4 
        assert database().scheduler_data_count(Cramming.WRONG) == 0
        card = scheduler().get_next_card()
        scheduler().grade_answer(card, 0)
        database().update_card(card)
        assert database().scheduler_data_count(Cramming.UNSEEN) == 3 
        assert database().scheduler_data_count(Cramming.WRONG) == 1
        card = scheduler().get_next_card()
        scheduler().grade_answer(card, 5)
        database().update_card(card)
        assert database().scheduler_data_count(Cramming.UNSEEN) == 2
        assert database().scheduler_data_count(Cramming.WRONG) == 1
        # Fail the cards a couple of times.
        for i in range(8):
            card = scheduler().get_next_card()
            scheduler().grade_answer(card, 0)
            database().update_card(card)
        # Pass the cards a couple of times.
        for i in range(8):
            card = scheduler().get_next_card()
            scheduler().grade_answer(card, 5)
            database().update_card(card)
 
    def test_2(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]

        ui_controller_review().new_question()
        ui_controller_main().delete_current_fact()
        assert ui_controller_review().card == None

    def test_3(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]

        ui_controller_review().new_question()

        self.mnemosyne.finalise()
        self.mnemosyne.initialise(os.path.abspath("dot_test"))

        assert scheduler().name == "cramming"
        
    def test_4(self):
        card_type = card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]

        ui_controller_review().new_question()
        database().unload()
        ui_controller_review().reset()
