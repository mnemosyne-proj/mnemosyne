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

        for c in self.database().cards_from_fact(fact):
            assert c.extra_data["cloze"] in c.fact["text"]

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        fact_data = {"text": "a_ [b_]"}
        self.controller().edit_sister_cards(fact, fact_data, card.card_type,
               card_type, new_tag_names=["default2"], correspondence=[])

        for c in self.database().cards_from_fact(fact):
            assert c.extra_data["cloze"] in c.fact["text"]

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        fact_data = {"text": "a_ [b_] [d] [e]"}
        self.controller().edit_sister_cards(fact, fact_data, card.card_type,
               card_type, new_tag_names=["default2"], correspondence=[])

        for c in self.database().cards_from_fact(fact):
            assert c.extra_data["cloze"] in c.fact["text"]

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

    def test_overlap(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": "[as] [a]"}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        assert "[...] a" in cards[0].question()
        assert "as [...]" in cards[1].question()

        fact_data = {"text": "[buds] [bud]"}
        self.controller().edit_sister_cards(fact, fact_data, card_type,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)

        assert "[...] bud" in cards[0].question()
        assert "buds [...]" in cards[1].question()

    def test_overlap_2(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": "[as] [a]"}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        assert "[...] a" in cards[0].question()
        assert "as [...]" in cards[1].question()

        fact_data = {"text": "[as] [bud]"}
        self.controller().edit_sister_cards(fact, fact_data, card_type,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)

        assert "[...] bud" in cards[0].question()
        assert "as [...]" in cards[1].question()

    def test_overlap_3(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": "[as] [a]"}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact
        assert "[...] a" in cards[0].question()
        assert "as [...]" in cards[1].question()

        fact_data = {"text": "[buds] [a]"}
        self.controller().edit_sister_cards(fact, fact_data, card_type,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)

        assert "[...] a" in cards[0].question()
        assert "buds [...]" in cards[1].question()

    def test_edit_2(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": "[consumerist] lifestyles"}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])
        fact = cards[0].fact

        fact_data = {"text": "[consumerism]"}
        self.controller().edit_sister_cards(fact, fact_data, card_type,
            card_type, new_tag_names=["default"], correspondence={})
        cards = self.database().cards_from_fact(fact)

        question = cards[0].question()
        print question, cards[0].extra_data, cards[0].fact.data
        assert "[...]" in question
        assert "consumerism" not in question
        assert "consumerist" not in question
        assert "lifestyles" not in question

    def test_duplicate(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": "[a] [a]"}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        assert "[...] a" in cards[0].question()
        assert "a [...]" in cards[1].question()
        
    def test_henrik_1(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": """I [1302] ble [Ingebjorg] (datteren til [Eufemia]
og [Hakon V]) lovet bort til hertug [Erik] av [Sverige]. Hun var da [ett] ar
gammel...."""}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        for card in cards:
            assert card.question().count("[") == 1

    def test_henrik_2(self):
        card_type = self.card_type_with_id("5")
        fact_data = {"text": """Since his death in [1992], [Francis Bacon]'s
reputation has steadily
grown. Despite [Margaret Thatcher] having famously described him as
"that man who paints those [dreadful pictures]", he was the subject of
two major [Tate retrospectives] during his lifetime and received a
third in 2008"""}

        cards = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        for card in cards:
            assert card.question().count("[") == 1