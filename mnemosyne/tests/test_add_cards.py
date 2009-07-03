#
# test_add_cards.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class Widget(MainWidget):

    def information_box(self, message):
        if message == "Card is already in database.\nDuplicate not added.":
            return 0
        raise NotImplementedError


class TestAddCards(MnemosyneTest):


    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_add_cards", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))


    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        assert self.database().average_easiness() == 2.5

    def test_1_duplicates(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
    def test_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("2")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
    def test_3(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = self.card_type_by_id("3")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

    def test_delete(self):
        fact_data = {"q": "question1",
                     "a": "answer1"}
        card_type = self.card_type_by_id("1")
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        assert set(tag.name for tag in card_1.tags) == \
               set(tag.name for tag in card_2.tags)
        fact_data = {"q": "question3",
                     "a": "answer3"}
        card_3 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              grade=-1, tag_names=["default"])[0]
        self.ui_controller_review().new_question()
        assert self.ui_controller_review().card == card_1
        self.ui_controller_review().grade_answer(0)
        self.database().delete_fact_and_related_data(card_3.fact)
        self.ui_controller_review().rebuild_queue()
        self.ui_controller_review().new_question() 
        for i in range(6):
            assert self.ui_controller_review().card != card_3
            self.ui_controller_review().grade_answer(0)        

    def test_change_tag(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        self.ui_controller_review().new_question()
        self.ui_controller_main().update_related_cards(card.fact, fact_data, \
            card_type, ["new"], correspondence={})     
        new_card = self.database().get_card(card._id)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "new" in tag_names
