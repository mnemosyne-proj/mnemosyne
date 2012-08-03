#
# test_mnemosyne2cards.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class TestMnemosyne2Cards(MnemosyneTest):

    def cards_format(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne2Cards":
                return format

    def test_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_2 = self.card_type_with_id("2")
        card_1, card_2 = self.controller().create_new_cards(\
            fact_data, card_type_2, grade=-1, tag_names=["default"])
        self.database().save()

        filename = os.path.join(os.getcwd(), "tests", "files", "bad_version.xml")
        self.cards_format().do_export("test.cards")



    def teardown(self):
        if os.path.exists("test.cards"):
            os.remove("test.cards")