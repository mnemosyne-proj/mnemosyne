#
# test_convert_cards.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import copy
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):

    def show_question(self, question, option0, option1, option2):
        if question.startswith("This will delete cards and their history"):
            return 0  # Proceed and delete":
        if question.startswith("Can't preserve history when converting"):
            return 0  # Reset learning history
        if question.startswith("Identical card is already in database"):
            return  0 # Do not add
        raise NotImplementedError


class TestConverter:

    def test(self):
        c = CardTypeConverter(None)
        new_cards, edited_cards, deleted_cards \
                   = c.convert(None, None, None, None)
        assert new_cards == []
        assert edited_cards == []
        assert deleted_cards == []

class TestConvertCards(MnemosyneTest):

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
            ("test_convert_cards", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

        from mnemosyne.libmnemosyne.card_types.map import MapPlugin
        for plugin in self.plugins():
            if isinstance(plugin, MapPlugin):
                plugin.activate()
                break

    def test_1_to_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])

        new_fact_data = {"f": "question2",
                         "b": "answer2"}
        new_card_type = self.card_type_with_id("2")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.card_type.id == "2"
        assert new_card_2.card_type.id == "2"

        if new_card_1.fact_view.id == "2.1":
            print(new_card_1.id, new_card_2.id, old_card.id)
            assert new_card_1 == old_card
            assert new_card_2 != old_card
            assert new_card_2.grade == -1
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card
            assert new_card_1.grade == -1

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_1_to_2_multi(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}

        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])

        new_fact_data = {"f": "question2",
                         "b": "answer2"}
        new_card_type = self.card_type_with_id("2")
        self.controller().change_card_type([fact], card.card_type,
               new_card_type, correspondence=[])

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.card_type.id == "2"
        assert new_card_2.card_type.id == "2"

        if new_card_1.fact_view.id == "2.1":
            assert new_card_1 == old_card
            assert new_card_2 != old_card
            assert new_card_2.grade == -1
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card
            assert new_card_1.grade == -1

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_1_to_2_multi_no_media(self):
        fact_data = {"f": "question",
                     "b": "answer"}

        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])

        new_fact_data = {"f": "question2",
                         "b": "answer2"}
        new_card_type = self.card_type_with_id("2")
        self.controller().change_card_type([fact], card.card_type,
               new_card_type, correspondence=[])

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.card_type.id == "2"
        assert new_card_2.card_type.id == "2"

        if new_card_1.fact_view.id == "2.1":
            assert new_card_1 == old_card
            assert new_card_2 != old_card
            assert new_card_2.grade == -1
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card
            assert new_card_1.grade == -1

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_2_to_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("2")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question2",
                         "b": "answer2"}
        new_card_type = self.card_type_with_id("1")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1"

        if old_card_1.fact_view.id == "2.1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_1_to_3_a(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])

        new_fact_data = {"f": "foreign word",
                         "p_1": "pronunciation",
                         "m_1": "translation"}
        correspondence = {"f": "f", "b": "p_1"}
        new_card_type = self.card_type_with_id("3")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.card_type.id == "3"
        assert new_card_2.card_type.id == "3"

        if new_card_1.fact_view.id == "3.1":
            assert new_card_1 == old_card
            assert new_card_2 != old_card
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_1_to_3_b(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])

        new_fact_data = {"f": "foreign word",
                         "p_1": "pronunciation",
                         "m_1": "translation"}
        correspondence = {"f": "m_1", "b": "f"}
        new_card_type = self.card_type_with_id("3")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.card_type.id == "3"
        assert new_card_2.card_type.id == "3"

        if new_card_1.fact_view.id == "3.2":
            assert new_card_1 == old_card
            assert new_card_2 != old_card
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_3_to_1_a(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "f", "m_1": "b"}
        new_card_type = self.card_type_with_id("1")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1"

        if old_card_1.fact_view.id == "3.1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_3_to_1_b(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "b", "m_1": "f"}
        new_card_type = self.card_type_with_id("1")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1"

        if old_card_1.fact_view.id == "3.2":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_3_to_1_c(self):
        # Missing required field.
        fact_data = {"f": "foreign word",
                     "m_1": "meaning"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"b": "foreign word"}
        correspondence = {"f": "b", "p_1": "f"}
        new_card_type = self.card_type_with_id("1")
        self.controller().change_card_type([fact], card_type,
               new_card_type, correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        card_1, card_2 = self.database().cards_from_fact(fact)
        assert card_1.card_type.id == "3"
        assert card_2.card_type.id == "3"


    def test_2_to_3_a(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("2")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "foreign word",
                         "p_1": "pronunciation",
                         "m_1": "translation"}
        correspondence = {"f": "f", "b": "m_1"}
        new_card_type = self.card_type_with_id("3")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.card_type.id == "3"
        assert new_card_2.card_type.id == "3"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view.id.split(".")[1] == \
                           new.fact_view.id.split(".")[1]

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_2_to_3_b(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("2")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "foreign word",
                         "p_1": "pronunciation",
                         "m_1": "translation"}
        correspondence = {"f": "m_1", "b": "f"}
        new_card_type = self.card_type_with_id("3")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.card_type.id == "3"
        assert new_card_2.card_type.id == "3"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view != new.fact_view

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_3_to_2_a(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "f", "m_1": "b"}
        new_card_type = self.card_type_with_id("2")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.card_type.id == "2"
        assert new_card_2.card_type.id == "2"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view.id.split(".")[1] == \
                           new.fact_view.id.split(".")[1]

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_3_to_2_b(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "b", "m_1": "f"}
        new_card_type = self.card_type_with_id("2")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.card_type.id == "2"
        assert new_card_2.card_type.id == "2"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view != new.fact_view

        new_card_1.question()
        new_card_1.answer()
        new_card_2.question()
        new_card_2.answer()

    def test_3_clone_to_1_a(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_with_id("3::my_3")

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "f", "m_1": "b"}
        new_card_type = self.card_type_with_id("1")
        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1"

        if old_card_1.fact_view.id == "3::my_3.1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_3_to_1_clone_a(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "f", "m_1": "b"}
        new_card_type = self.card_type_with_id("1")
        self.controller().clone_card_type(new_card_type, "my_1")
        new_card_type = self.card_type_with_id("1::my_1")

        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1::my_1"
        assert new_card.fact.data["f"] == "question"
        assert new_card.fact.data["b"] == "answer"

        if old_card_1.fact_view.id == "3.1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_3_clone_to_1_clone_a(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_with_id("3::my_3")

        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"f": "question",
                         "b": "answer"}
        correspondence = {"f": "f", "m_1": "b"}
        new_card_type = self.card_type_with_id("1")
        self.controller().clone_card_type(new_card_type, "my_1")
        new_card_type = self.card_type_with_id("1::my_1")

        self.controller().edit_card_and_sisters(card, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.card_type.id == "1::my_1"

        if old_card_1.fact_view.id == "3::my_3.1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1

        new_card.question()
        new_card.answer()

    def test_cloze_to_1(self):
        from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
             StatisticsWidget
        from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
        class ScheduleWdgt(StatisticsWidget):
            used_for = Schedule
        self.mnemosyne.component_manager.register(ScheduleWdgt)

        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "5":
                plugin.activate()

        fact_data = {"text": "[question]"}
        card_type = self.card_type_with_id("5")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.review_controller().reset()

        new_card_type = self.card_type_with_id("1")
        fact_data = {"f": "[question]", "b": ""}
        self.controller().edit_card_and_sisters(card, fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence={'text': "f"})

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(card.fact)[0]

        new_card.question()
        new_card.answer()

    def test_2_to_2_clone(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("2")
        card_1, card_2  = self.controller().create_new_cards(fact_data,
                                 card_type, grade=-1, tag_names=["default"])

        new_card_type = self.controller().\
                        clone_card_type(card_type, "my_2")

        self.controller().edit_card_and_sisters(card_1, fact_data,
               new_card_type, new_tag_names=["default"],
               correspondence={})

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card = self.database().cards_from_fact(card_1.fact)[0]
        assert new_card.card_type.id == "2::my_2"
        assert new_card.fact.data["f"] == "question"
        assert new_card.fact.data["b"] == "answer"

        new_card.question()
        new_card.answer()

    def test_1_to_3_clone(self):
        card_type = self.card_type_with_id("1") # Production only.
        fact_data = {"f": "translation",
                     "b": "foreign"}
        card = self.controller().create_new_cards(fact_data,
            card_type, grade=2, tag_names=["default"])[0]

        new_card_type = self.controller().\
                        clone_card_type(self.card_type_with_id("3"), "my_language")
        correspondence = {"f": "m_1", "b": "f"}
        self.controller().change_card_type([card.fact], card_type, new_card_type,
                         correspondence=correspondence)

        fact = self.database().fact(card.fact._id, is_id_internal=True)
        assert fact["f"] == "foreign"
        card_1, card_2 = self.database().cards_from_fact(fact)

        assert len(card_1.tags) == 1
        assert len(card_2.tags) == 1
        for tag in card_1.tags:
            assert tag.name == "default"
        for tag in card_2.tags:
            assert tag.name == "default"

        assert self.database().con.execute("select tags from cards where _id=?",
            (card_1._id, )).fetchone()[0] == "default"
        assert self.database().con.execute("select tags from cards where _id=?",
            (card_2._id, )).fetchone()[0] == "default"

        assert card_1.active == True
        assert card_2.active == True

        if card_1.fact_view.id == "3.1": # Recognition
            assert "foreign" in  card_1.question()
            assert "translation" in card_2.question()
            assert card_1.grade == -1
            assert card_2.grade == 2
        else:
            assert "foreign" in  card_2.question()
            assert "translation" in card_1.question()
            assert card_2.grade == -1
            assert card_1.grade == 2

    def test_1_to_3_clone_bis(self):
        card_type = self.card_type_with_id("1") # Production only.
        fact_data = {"f": "translation",
                     "b": "foreign"}
        card = self.controller().create_new_cards(fact_data,
            card_type, grade=2, tag_names=["default"])[0]

        new_card_type = self.controller().\
                        clone_card_type(self.card_type_with_id("3"), "my_language")
        correspondence = {"f": "m_1", "b": "f"}

        new_fact_data = {"m_1": "translation", "f": "foreign"}

        self.controller().edit_card_and_sisters(card, new_fact_data,
            new_card_type, new_tag_names=["default"], correspondence=correspondence)

        fact = self.database().fact(card.fact._id, is_id_internal=True)
        assert fact["f"] == "foreign"
        card_1, card_2 = self.database().cards_from_fact(fact)

        assert len(card_1.tags) == 1
        assert len(card_2.tags) == 1
        for tag in card_1.tags:
            assert tag.name == "default"
        for tag in card_2.tags:
            assert tag.name == "default"

        assert self.database().con.execute("select tags from cards where _id=?",
            (card_1._id, )).fetchone()[0] == "default"
        assert self.database().con.execute("select tags from cards where _id=?",
            (card_2._id, )).fetchone()[0] == "default"

        assert card_1.active == True
        assert card_2.active == True

        print(card_1.grade, card_2.grade)

        if card_1.fact_view.id == "3::my_language.1": # Recognition
            assert "foreign" in card_1.question()
            assert "translation" in card_2.question()
            assert card_1.grade == -1
            assert card_2.grade == 2
        else:
            assert "foreign" in card_2.question()
            assert "translation" in card_1.question()
            assert card_2.grade == -1
            assert card_1.grade == 2

    def test_convert_duplicates(self):
        card_type_map = self.card_type_with_id("4")
        fact_data = {"loc": "test",
                     "blank": "test1",
                     "marked": "test2"}
        card = self.controller().create_new_cards(fact_data,
            card_type_map, grade=2, tag_names=["default"])[0]

        card_type = self.card_type_with_id("1")
        fact_data = {"f": "test1",
                     "b": "test2"}
        card = self.controller().create_new_cards(fact_data,
            card_type, grade=2, tag_names=["default"])[0]

        correspondence = {"f": "blank", "b": "marked"}

        new_fact_data = {"loc": "test",
                     "blank": "test1",
                     "marked": "test2"}

        self.controller().edit_card_and_sisters(card, new_fact_data,
            card_type_map, new_tag_names=["default"], correspondence=correspondence)

    def teardown_method(self):
        if os.path.exists("a.ogg"):
            os.remove("a.ogg")
        MnemosyneTest.teardown_method(self)
