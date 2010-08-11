#
# test_cramming.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class Widget(MainWidget):

    def question_box(self, question, option0, option1, option2):
        if option0 == "&Delete":
            return 0
        raise NotImplementedError


class TestCrammingScheduler(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_cramming", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)

        from mnemosyne.libmnemosyne.plugins.cramming_plugin import CrammingPlugin
        for plugin in self.plugins():
            if isinstance(plugin, CrammingPlugin):
                plugin.activate()
                break
        self.review_controller().reset()
        
    def test_1(self):
        from mnemosyne.libmnemosyne.schedulers.cramming import Cramming
        
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
        card_4.next_rep -= 1000
        self.database().edit_card(card_4)

        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 4 
        assert self.database().scheduler_data_count(Cramming.WRONG) == 0
        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 0)
        self.database().edit_card(card)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 3 
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 5)
        self.database().edit_card(card)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 2
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        # Fail the cards a couple of times.
        for i in range(8):
            card = self.scheduler().next_card()
            self.scheduler().grade_answer(card, 0)
            self.database().edit_card(card)
        # Pass the cards a couple of times.
        for i in range(8):
            card = self.scheduler().next_card()
            self.scheduler().grade_answer(card, 5)
            self.database().edit_card(card)
 
    def test_2(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().new_question()
        self.controller().delete_current_fact()
        assert self.review_controller().card == None

    def test_3(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().new_question()

        self.mnemosyne.finalise()
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)

        assert self.scheduler().name == "cramming"
        
    def test_4(self):
        card_type = self.card_type_by_id("1")
        
        fact_data = {"q": "1", "a": "a"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().new_question()
        self.database().unload()
        self.review_controller().reset()
        self.restart()
