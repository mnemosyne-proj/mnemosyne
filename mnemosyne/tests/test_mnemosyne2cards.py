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

    def test_tag(self):
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
        self.cards_format().do_import("test.cards")
        self.database().save()
        assert len([c for c in self.database().cards()]) == 2
        for _card_id, _fact_id in self.database().cards():
            card = self.database().card(_card_id, is_id_internal=True)
            assert card.active == True
            assert card.id

    def test_card_type(self):
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
        self.cards_format().do_import("test.cards")
        self.database().save()
        assert len([c for c in self.database().cards()]) == 1

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

    def test_rename_tags(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import("test.cards")
        assert len(self.database().tags()) == 2
        tag = self.database().get_or_create_tag_with_name("default")
        tag.name = "edited"
        self.database().update_tag(tag)
        assert self.database().tags()[0].name == "edited"
        self.cards_format().do_import("test.cards")
        assert self.database().tags()[0].name == "default"

    def test_existing_card_type(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        assert len(self.card_types()) == 3
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert len(self.card_types()) == 4
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        assert len(self.card_types()) == 5
        card_type.extra_data = {1:1}
        card_type.fact_views[0].extra_data = {2:2}
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        assert len(self.card_types()) == 3
        card_type = self.card_type_with_id("1")
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))

        assert len(self.card_types()) == 4
        self.cards_format().do_import("test.cards")
        assert len(self.card_types()) == 6
        self.cards_format().do_import("test.cards")
        assert len(self.card_types()) == 6

    def test_rename_card_type(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        assert len(self.card_types()) == 3
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert len(self.card_types()) == 4
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        assert len(self.card_types()) == 5
        card_type.extra_data = {1:1}
        card_type.fact_views[0].extra_data = {2:2}
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        self.cards_format().do_import("test.cards")
        assert len(self.card_types()) == 5
        card_type = self.card_type_with_id("1::1 clone")
        card_type.name = "renamed"
        self.database().update_card_type(card_type)
        assert "renamed" in [card_type.name for card_type in self.card_types()]
        self.cards_format().do_import("test.cards")
        assert len(self.card_types()) == 5
        assert "renamed" not in [card_type.name for card_type in self.card_types()]
        self.cards_format().do_import("test.cards")
        assert len(self.card_types()) == 5
        assert "renamed" not in [card_type.name for card_type in self.card_types()]

    def test_update_fact(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])

        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        self.cards_format().do_import("test.cards")
        _card_id, _fact_id = self.database().cards().next()
        card = self.database().card(_card_id, is_id_internal=True)
        card.fact["f"] = "edited"
        self.database().update_fact(card.fact)
        assert "edited" in card.question()
        self.cards_format().do_import("test.cards")
        _card_id, _fact_id = self.database().cards().next()
        card = self.database().card(_card_id, is_id_internal=True)
        assert "edited" not in card.question()

    def test_media(self):
        filename_a = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", unichr(0x628) + u"a.ogg")
        f = file(filename_a, "w")
        print >> f, "a"
        f.close()
        os.mkdir(os.path.join(os.path.abspath("dot_test"),
        "default.db_media", "b"))
        filename_b = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", "b", unichr(0x628) + u"b.ogg")
        f = file(filename_b, "w")
        print >> f, "b"
        f.close()

        fact_data = {"f": "question\n<img src=\"%s\">" % (filename_a),
                     "b": "question\n<img src=\"%s\">" % (filename_b)}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.cards_format().do_export("test.cards")

        self.database().new("import.db")
        self.cards_format().do_import("test.cards")
        assert os.path.exists(os.path.join("dot_test", "import.db_media",
            unichr(0x628) + u"a.ogg"))
        assert os.path.exists(os.path.join("dot_test", "import.db_media",
            "b", unichr(0x628) + u"b.ogg"))

    def teardown(self):
        if os.path.exists("test.cards"):
            os.remove("test.cards")
        MnemosyneTest.teardown(self)