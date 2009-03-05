#
# test_html_css.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main


class TestHtmlCss:

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
        
        fact = list(database().cards_unseen())[0].fact
        card = database().cards_from_fact(fact)[0]

        assert card.question() == """<html><head><style type="text/css">
        table { height: 100%; margin-left: auto; margin-right: auto;  }
body { margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }
div#q { text-align: center; }
div#a { text-align: center; }
</style></head><body><table><tr><td><div id="q">question</div></td></tr></table></body></html>"""

        assert card.answer() == """<html><head><style type="text/css">
        table { height: 100%; margin-left: auto; margin-right: auto;  }
body { margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }
div#q { text-align: center; }
div#a { text-align: center; }
</style></head><body><table><tr><td><div id="a">answer</div></td></tr></table></body></html>"""
        
    def teardown(self):
         finalise()
