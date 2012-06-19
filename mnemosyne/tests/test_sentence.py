#
# test_sentence.py <Peter.Bienstman@UGent.be>
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


class TestSentence(MnemosyneTest):

    def setup(self):
        shutil.rmtree("dot_test", ignore_errors=True)

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_cloze", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
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
