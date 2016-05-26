#
# test_html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestHtmlCss(MnemosyneTest):

    def test_1(self):
        self.config()["font"] = {'1': {"f": 'Courier New,10,-1,5,50,1,0,0,0,0',
                                       "b": 'Courier New,10,-1,5,25,2,0,0,0,0'},
                                 '3': {'p': 'Courier New,10,-1,5,75,0,0,0,0,0',
                                       't': 'Courier New,10,-1,5,50,0,0,0,0,0',
                                       'f': 'Courier New,10,-1,5,50,0,0,0,0,0'},
                                 '2': {"f": 'Courier New,10,-1,5,50,0,1,0,0,0',
                                       "b": 'Courier New,10,-1,5,50,0,0,1,0,0'}}
        self.config()["alignment"] = {'1': 'right', '3': 'center', '2': 'left'}
        self.config()["background_colour"] = {'1': 4278255615, '3': 4278255615, '2': 4278255615}
        self.config()["font_colour"] = {'1': {"f": 4290772992, "b": 4290772992},
                                      '3': {'p': 4290772992, 't': 4290772992, 'f': 4290772992},
                                      '2': {"f": 4290772992, "b": 4290772992}}

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        card_type = self.card_type_with_id("2")
        card2 = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question", "p_1": "",
                     "m_1": "answer"}
        card_type = self.card_type_with_id("3")
        card3 = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        card.question()
        card.answer()
        card.question("sync_to_card_only_client")
        card.question("card_browser")
        card.question("card_browser", ignore_text_colour=True)

        card2.question()
        card2.answer()
        card2.question("sync_to_card_only_client")
        card2.question("card_browser")
        card2.question("card_browser", ignore_text_colour=True)

        card3.question()
        card3.answer()
        card3.question("sync_to_card_only_client")
        card3.question("card_browser")
        card3.question("card_browser", ignore_text_colour=True)
        card3.question("card_browser", search_string="(")
        card3.question("card_browser", search_string="\\")

    def test_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        card_type = self.card_type_with_id("2")
        card2 = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question", "p_1": "",
                     "m_1": "answer"}
        card_type = self.card_type_with_id("3")
        card3 = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        card.question()
        card.answer()
        card.question("sync_to_card_only_client")
        card.question("card_browser")
        card.question("card_browser", ignore_text_colour=True)
        card.question("card_browser", ignore_text_colour=True, search_string="e")

        card2.question()
        card2.answer()
        card2.question("sync_to_card_only_client")
        card2.question("card_browser")
        card2.question("card_browser", ignore_text_colour=True)
        card2.question("card_browser", ignore_text_colour=True, search_string="e")

        card3.question()
        card3.answer()
        card3.question("sync_to_card_only_client")
        card3.question("card_browser")
        card3.question("card_browser", ignore_text_colour=True)
        card3.question("card_browser", ignore_text_colour=True, search_string="e")
