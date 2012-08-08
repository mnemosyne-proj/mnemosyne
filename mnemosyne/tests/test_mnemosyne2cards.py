#
# test_mnemosyne2cards.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne


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

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import("test.cards")
        self.database().save()
        assert len([c for c in self.database().cards()]) == 2
        for _card_id, _fact_id in self.database().cards():
            card = self.database().card(_card_id, is_id_internal=True)
            assert card.active == True
            assert card.id

    def test_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        card_type.extra_data = {1:1}
        card_type.fact_views[0].extra_data = {2:2}
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import("test.cards")
        self.database().save()
        assert len([c for c in self.database().cards()]) == 1
        for _card_id, _fact_id in self.database().cards():
            card = self.database().card(_card_id, is_id_internal=True)
            assert card.active == True
            assert card.id

    def test_existing_tag(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.database().get_or_create_tag_with_name("default")
        assert len(self.database().tags()) == 2
        self.cards_format().do_import("test.cards")
        assert len(self.database().tags()) == 3
        self.cards_format().do_import("test.cards")
        assert len(self.database().tags()) == 3

    def teardown(self):
        if os.path.exists("test.cards"):
            os.remove("test.cards")
        MnemosyneTest.teardown(self)