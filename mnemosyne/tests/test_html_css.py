#
# test_html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestHtmlCss(MnemosyneTest):
     
    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        self.ui_controller_main().file_save()
        
        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]

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
        
