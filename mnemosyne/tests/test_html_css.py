#
# test_html_css.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestHtmlCss(MnemosyneTest):
     
    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()
        
        fact = card.fact
        card = self.database().cards_from_fact(fact)[0]

        card.question()
        card.answer()

        card.question("sync_to_card_only_client")
