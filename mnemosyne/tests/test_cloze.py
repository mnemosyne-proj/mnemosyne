#
# test_cloze.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.card_types.cloze import Cloze
from mnemosyne.libmnemosyne.component_manager import database 
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_main

class TestCloze:

    def setup(self):
        os.system("rm -fr dot_test")
        initialise(os.path.abspath("dot_test"))
        p = Cloze()
        component_manager.register("plugin", p)
        p.activate()

    def test_validate(self):
        card_type = card_type_by_id("5")
        
        fact_data = {"text": "incomplete"}
        assert card_type.validate_data(fact_data) == False
        
        fact_data = {"text": "[incomplete"}
        assert card_type.validate_data(fact_data) == False
        
        fact_data = {"text": "incomplete]"}
        assert card_type.validate_data(fact_data) == False
        
        fact_data = {"text": "[]"}
        assert card_type.validate_data(fact_data) == False
        
        fact_data = {"text": "[complete]"}
        assert card_type.validate_data(fact_data) == True

    def test_add(self):
        card_type = card_type_by_id("5")
        
        fact_data = {"text": "a [b] c"}

        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card = database().cards_from_fact(fact)[0]
        
        assert database().fact_count() == 1
        assert database().card_count() == 1

        assert card.question() == """<html><head><style type="text/css">
        table { height: 100%; margin-left: auto; margin-right: auto;  }
body { margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }
div#text { text-align: center; }
</style></head><body><table><tr><td><div id="%s"><div id="text">a [...] c</div></td></tr></table></body></html>"""
        
        assert card.answer() == """<html><head><style type="text/css">
        table { height: 100%; margin-left: auto; margin-right: auto;  }
body { margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }
div#text { text-align: center; }
</style></head><body><table><tr><td><div id="%s"><div id="text">b</div></td></tr></table></body></html>"""
        
    def test_update(self):
        card_type = card_type_by_id("5")
        
        fact_data = {"text": "a [b] [c]"}

        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card = database().cards_from_fact(fact)[0]
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        fact_data = {"text": "a_ [b_] [c_]"}
        ui_controller_main().update_related_cards(fact, fact_data,
               card_type, new_cat_names=["default2"], correspondence=[])
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        fact_data = {"text": "a_ [b_]"}
        ui_controller_main().update_related_cards(fact, fact_data,
               card_type, new_cat_names=["default2"], correspondence=[])
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        fact_data = {"text": "a_ [b_] [d] [e]"}
        ui_controller_main().update_related_cards(fact, fact_data,
               card_type, new_cat_names=["default2"], correspondence=[])
        
        assert database().fact_count() == 1
        assert database().card_count() == 3
        
    def teardown(self):
        finalise()
