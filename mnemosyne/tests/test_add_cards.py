#
# test_add_cards.py <Peter.Bienstman@UGent.be>
#

import os
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

answer = 0

class Widget(MainWidget):

    def show_information(self, message):
        if message == "Card is already in database.\nDuplicate not added.":
            return 0
        raise NotImplementedError

    def show_question(self, question, a, b, c):
        if question.startswith("Delete"):
            return 0
        else:
            return answer


class TestAddCards(MnemosyneTest):

    def setup(self):
        shutil.rmtree("dot_test", ignore_errors=True)

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_add_cards", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditCardDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

    def test_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        assert self.database().is_in_use(card_type) is True
        self.controller().save_file()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_coverage(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        card.fact["f"] = "new_question"


    def test_src(self):
        fact_data = {"f": """<font face="courier">src</font>""",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        card.question()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_comparisons(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        assert card == card
        assert card.fact == card.fact
        assert card.fact_view == card.fact_view

        class A(object):
            pass
        a = A()
        assert card != a
        assert card.fact != a
        assert card.fact_view != a
        tag = card.tags.pop()
        assert tag == tag
        assert tag != a

    def test_1_duplicates(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("2")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

    def test_3(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

    def test_delete(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        assert set(tag.name for tag in card_1.tags) == \
               set(tag.name for tag in card_2.tags)
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(0)
        self.controller().delete_facts_and_their_cards([card_3.fact])
        self.review_controller().reset()
        for i in range(6):
            assert self.review_controller().card != card_3
            self.review_controller().grade_answer(0)

    def test_delete_2(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        assert set(tag.name for tag in card_1.tags) == \
               set(tag.name for tag in card_2.tags)
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.controller().delete_current_card()
        for i in range(6):
            assert self.review_controller().card != card_1
            self.review_controller().grade_answer(0)

    def test_change_tag(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        self.controller().edit_sister_cards(card.fact, fact_data, card.card_type,
            card_type, ["new"], correspondence={})
        new_card = self.database().card(card._id, is_id_internal=True)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "new" in tag_names

    def test_untagged(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1

    def test_edit_untagged(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag"])[0]
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1

        self.controller().edit_sister_cards(new_card.fact, new_card.fact.data,
           card.card_type,  new_card.card_type, [" "], [])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1

    def test_edit_untagged_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[""])[0]
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().card(card._id, is_id_internal=True)
        _untagged_id =  list(new_card.tags)[0]._id

        self.controller().edit_sister_cards(new_card.fact, new_card.fact.data,
           card.card_type,  new_card.card_type, ["tag"], [])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert list(new_card.tags)[0]._id != _untagged_id

    def test_duplicate(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag"])[0]
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["tag"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_duplicate_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag"])[0]
        global answer
        answer = 0  # Merge.
        fact_data = {"f": "question",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["tag"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_duplicate_3(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag"])[0]
        fact_data = {"f": "question",
                     "b": "answer2"}
        global answer
        answer = 1 # Add.
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["tag"])
        assert self.database().fact_count() == 2
        assert self.database().card_count() == 2

    def test_duplicate_4(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag"])[0]
        fact_data = {"f": "question",
                     "b": "answer2"}
        global answer
        answer = 2 # Don't add.
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["tag"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

    def test_log(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=3, tag_names=["default"])[0]
        self.controller().save_file()

        sql_res = self.database().con.execute(\
            "select * from log where _id=14").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_CARD
        assert sql_res["object_id"] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=15").fetchone()
        assert sql_res["event_type"] == EventTypes.REPETITION

    def test_optional_keys(self):
        fact_data = {"f": "foreign",
                     "m_1": "meaning", "n": ""}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=3, tag_names=["default"])[0]
        self.controller().save_file()
        assert self.database().con.execute(\
            "select count() from data_for_fact where key='n'").fetchone()[0] == 0

        fact_data_2 = {"f": "foreign",
                       "m_1": "meaning", "n": "notes"}
        self.controller().edit_sister_cards(card.fact, fact_data_2, card_type,
            card_type, [], {})
        self.controller().save_file()
        assert self.database().con.execute(\
            "select count() from data_for_fact where key='n'").fetchone()[0] == 1

        self.controller().edit_sister_cards(card.fact, fact_data, card_type,
            card_type, [], {})
        self.controller().save_file()
        assert self.database().con.execute(\
            "select count() from data_for_fact where key='n'").fetchone()[0] == 0
