#
# test_non_latin_font_size_increase.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml

    
class TestNonLatinFontSizeIncrease(MnemosyneTest):

    def test_1(self):
        fact_data = {"f": "question " + chr(40960),
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]

        self.config()["non_latin_font_size_increase"] = 2
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" in card.question()
        
    def test_2(self):
        fact_data = {"f": "<protect>question " + chr(40960) + "</protect>",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]

        self.config()["non_latin_font_size_increase"] = 2
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" not in card.question()

    def test_3(self):
        fact_data = {"f": "question " + chr(40960),
                     "p_1": "",
                     "m_1": "answer"}
        card_type = self.card_type_with_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]
        self.config()["non_latin_font_size_increase"] = 2
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" not in card.question()
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" not in card.answer()
        
    def test_4(self):
        fact_data = {"f": "question " + chr(40960),
                     "m_1": "answer"}
        card_type = self.card_type_with_id("3")
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_with_id("3::my_3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]

        self.config()["non_latin_font_size_increase"] = 2
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" not in card.question()
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" not in card.answer()
        
    def test_5(self):
        fact_data = {"f": "question " + chr(40960) + "tail",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=[])[0]

        self.config()["non_latin_font_size_increase"] = 2
        assert """<font style=\"font-size:14pt\">""" + chr(40960) + "</font>" in card.question()
