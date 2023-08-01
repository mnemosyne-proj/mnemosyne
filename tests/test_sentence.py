#
# test_sentence.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

answer = None

class Widget(MainWidget):

    def show_question(self, question, option0, option1, option2):
        return answer


class TestSentence(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_cloze", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

        from mnemosyne.libmnemosyne.card_types.sentence import SentencePlugin
        for plugin in self.plugins():
            if isinstance(plugin, SentencePlugin):
                plugin.activate()
                break

    def test_1(self):
        card_type = self.card_type_with_id("6")
        fact_data = {"f": "La [casa:house] es [grande:big]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        assert "La casa es grande" in cards[0].question()
        assert "La [house] es grande" in cards[1].question()
        assert "La casa es [big]" in cards[2].question()

    def test_2(self):
        card_type = self.card_type_with_id("6")
        fact_data = {"f": "[sentence]", "m_1": "meaning"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        assert "meaning" in cards[1].question()
        assert "[" not in cards[1].question()
        assert "meaning" not in cards[1].answer()

    def test_edit(self):
        card_type = self.card_type_with_id("6")
        fact_data = {"f": "La [casa:house] es [grande:big]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        fact_data = {"f": "[La casa es grande]"}
        self.controller().edit_card_and_sisters(cards[0], fact_data,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)
        assert len(cards) == 2

    def test_edit_2(self):
        card_type = self.card_type_with_id("6")
        fact_data = {"f": "La [casa:house] es [grande:big]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        fact_data = {"f": "[La casa] es grande"}
        self.controller().edit_card_and_sisters(cards[0], fact_data,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)
        assert len(cards) == 2

    def test_edit_3(self):
        card_type = self.card_type_with_id("6")
        fact_data = {"f": "La [casa:house] es [grande:big]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        fact_data = {"f": "[La casa] [es] [grande]"}
        self.controller().edit_card_and_sisters(cards[0], fact_data,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)
        assert len(cards) == 4
        for card in cards:
            assert card.card_type.id == "6"
        for card in cards[1:]:
            assert card.fact_view.id == "6.2"

    def test_clone(self):
        card_type = self.card_type_with_id("6")
        card_type = self.controller().clone_card_type(\
            card_type, ("6 clone"))
        fact_data = {"f": "La [casa:house] es [grande:big]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        assert "La casa es grande" in cards[0].question()
        assert "La [house] es grande" in cards[1].question()
        assert "La casa es [big]" in cards[2].question()

