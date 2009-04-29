#
# test_add_cards.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review


class TestAddCards(MnemosyneTest):

    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        assert database().fact_count() == 1
        assert database().card_count() == 1

        assert database().average_easiness() == 2.5

    def test_1_duplicates(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"],
                                              warn=False)
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
    def test_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
    def test_3(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        assert database().fact_count() == 1
        assert database().card_count() == 2

    def test_delete(self):
        fact_data = {"q": "question1",
                     "a": "answer1"}
        card_type = card_type_by_id("1")
        card_1 = ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, cat_names=["default"])[0]
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_2 = ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, cat_names=["default"])[0]
        fact_data = {"q": "question3",
                     "a": "answer3"}
        card_3 = ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, cat_names=["default"])[0]
        ui_controller_review().new_question()
        assert ui_controller_review().card == card_1
        ui_controller_review().grade_answer(0)
        database().delete_fact_and_related_data(card_3.fact)
        ui_controller_review().rebuild_queue()
        for i in range(6):
            ui_controller_review().new_question() 
            assert ui_controller_review().card != card_3
            ui_controller_review().grade_answer(0)        
