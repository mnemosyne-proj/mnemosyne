import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main


class TestAddCards:

    def setup(self):
        os.system("rm -fr dot_test")
        initialise(os.path.abspath("dot_test"))        

    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
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
        
    def teardown(self):
        finalise()
