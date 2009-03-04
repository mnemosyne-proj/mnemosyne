#
# test_convert_cards.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter

class TestConverter:

    def test(self):
        c = CardTypeConverter()
        new_cards, updated_cards, deleted_cards \
                   = c.convert(None, None, None, None)
        assert new_cards == []
        assert updated_cards == []
        assert deleted_cards == []

class TestConvertCards:

    def setup(self):
        os.system("rm -fr dot_test")
        initialise(os.path.abspath("dot_test"))        

    def test_1_to_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = card_type_by_id("2")     
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
    def test_2_to_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = card_type_by_id("1")
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[],
               warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1

    def test_1_to_3(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "p"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
    def test_3_to_1(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "p": "q"}
        new_card_type = card_type_by_id("1")     
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1

    def test_2_to_3(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "p"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
    def test_3_to_2(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "p": "q"}
        new_card_type = card_type_by_id("2")     
        ui_controller_main().update_related_cards(fact, fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
    def teardown(self):
        finalise()
