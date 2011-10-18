#
# test_cloze.py <Peter.Bienstman@UGent.be>
#

import os
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

answer = None

class Widget(MainWidget):

    def show_question(self, question, option0, option1, option2):
        return answer
    

class TestCloze(MnemosyneTest):

    def setup(self):
        shutil.rmtree("dot_test", ignore_errors=True)
        
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_cloze", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()
        
        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.plugins():
            if isinstance(plugin, ClozePlugin):
                plugin.activate()
                break

    def test_validate(self):
        card_type = self.card_type_with_id("5")
        
        fact_data = {"text": "incomplete"}
        assert card_type.is_fact_data_valid(fact_data) == False
        
        fact_data = {"text": "[incomplete"}
        assert card_type.is_fact_data_valid(fact_data) == False
        
        fact_data = {"text": "incomplete]"}
        assert card_type.is_fact_data_valid(fact_data) == False
        
        fact_data = {"text": "[]"}
        assert card_type.is_fact_data_valid(fact_data) == False
        
        fact_data = {"text": "[complete]"}
        assert card_type.is_fact_data_valid(fact_data) == True

    def test_add(self):
        card_type = self.card_type_with_id("5")
        
        fact_data = {"text": "a [b] c"}

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        assert "div#b { text-align: center; }" in card.question()
        assert "div#b { text-align: center; }" in card.answer()
        
    def test_edit(self):
        card_type = self.card_type_with_id("5")
        
        fact_data = {"text": "a [b] [c]"}

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        fact_data = {"text": "a_ [b_] [c_]"}
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        fact_data = {"text": "a_ [b_]"}
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        fact_data = {"text": "a_ [b_] [d] [e]"}
        self.controller().edit_sister_cards(fact, fact_data, card.card_type, 
               card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 3

    def test_convert(self):
        card_type = self.card_type_with_id("5")
        
        fact_data = {"text": "a [b] [c]"}

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]

        new_card_type = self.card_type_with_id("1")

        global answer
        answer = 0 # OK.
        self.controller().change_card_type([fact], card_type, new_card_type,
                         {'text': 'f'})

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
    def test_convert_abort(self):
        card_type = self.card_type_with_id("5")
        
        fact_data = {"text": "a [b] [c]"}

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]

        new_card_type = self.card_type_with_id("1")

        global answer
        answer = 1 # Cancel.
        self.controller().change_card_type([fact], card_type, new_card_type,
                         {'text': 'f'})

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
