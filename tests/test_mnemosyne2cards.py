#
# test_mnemosyne2cards.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportMetadataDialog

last_error = None

class MyMainWidget(MainWidget):

    def show_information(self, info):
        print(info)
        #sys.stderr.write(info+'\n')

    def show_error(self, error):
        global last_error
        last_error = error
        # Activate this for debugging.
        #sys.stderr.write(error)

    def show_question(self, question, option0, option1, option2):
        #sys.stderr.write(question+'\n')
        return answer


class Widget(ExportMetadataDialog):

    def values(self):
        return {}

    def set_read_only(self):
        pass


class TestMnemosyne2Cards(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_mnemosyne2cards", "Widget"))
        self.mnemosyne.components.append(\
            ("test_mnemosyne2cards", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.plugins():
            if isinstance(plugin, ClozePlugin):
                plugin.activate()
                break

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

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import(os.path.abspath("test.cards"))
        self.database().save()
        assert len([c for c in self.database().cards()]) == 2
        for _card_id, _fact_id in self.database().cards():
            card = self.database().card(_card_id, is_id_internal=True)
            assert card.active == True
            assert card.id
        self.cards_format().do_import(os.path.abspath("test.cards"), "tag1, tag2")
        self.database().save()
        assert len([tag.name for tag in self.database().tags()]) == 4
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

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import(os.path.abspath("test.cards"))
        self.database().save()
        assert len([c for c in self.database().cards()]) == 1
        for _card_id, _fact_id in self.database().cards():
            card = self.database().card(_card_id, is_id_internal=True)
            assert card.active == True
            assert card.id
        self.cards_format().do_import(os.path.abspath("test.cards"))
        self.database().save()
        assert len([c for c in self.database().cards()]) == 1

    def test_existing_tag(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.database().get_or_create_tag_with_name("default")
        assert len(self.database().tags()) == 2
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.database().tags()) == 3
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.database().tags()) == 3

    def test_rename_tags(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        assert len([c for c in self.database().cards()]) == 0
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.database().tags()) == 2
        tag = self.database().get_or_create_tag_with_name("default")
        tag.name = "edited"
        self.database().update_tag(tag)
        assert self.database().tags()[0].name == "edited"
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert self.database().tags()[0].name == "default"

    def test_existing_card_type(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        assert len(self.card_types()) == 5
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert len(self.card_types()) == 6
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        assert len(self.card_types()) == 7
        card_type.extra_data = {1:1}
        card_type.fact_views[0].extra_data = {2:2}
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        assert len(self.card_types()) == 5
        card_type = self.card_type_with_id("1")
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))

        assert len(self.card_types()) == 6
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.card_types()) == 8
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.card_types()) == 8

    def test_rename_card_type(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        assert len(self.card_types()) == 5
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert len(self.card_types()) == 6
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        assert len(self.card_types()) == 7
        card_type.extra_data = {1:1}
        card_type.fact_views[0].extra_data = {2:2}
        card_1 = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.database().save()

        filename = os.path.join(os.path.abspath("dot_test"), os.path.abspath("test.cards"))
        open(filename, "w")

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.card_types()) == 7
        card_type = self.card_type_with_id("1::1 clone")
        card_type.name = "renamed"
        self.database().update_card_type(card_type)
        assert "renamed" in [card_type.name for card_type in self.card_types()]
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.card_types()) == 7
        assert "renamed" not in [card_type.name for card_type in self.card_types()]
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert len(self.card_types()) == 7
        assert "renamed" not in [card_type.name for card_type in self.card_types()]

    def test_update_fact(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"))
        _card_id, _fact_id = next(self.database().cards())
        card = self.database().card(_card_id, is_id_internal=True)
        card.fact["f"] = "edited"
        self.database().update_fact(card.fact)
        assert "edited" in card.question()
        self.cards_format().do_import(os.path.abspath("test.cards"))
        _card_id, _fact_id = next(self.database().cards())
        card = self.database().card(_card_id, is_id_internal=True)
        assert "edited" not in card.question()

    def test_extra_tag(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=[])

        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"), "extra")
        _card_id, _fact_id = next(self.database().cards())
        card = self.database().card(_card_id, is_id_internal=True)
        assert len(card.tags) == 1
        assert card.tags.pop().name == "extra"

    def test_import_multiple(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])[0]
        self.cards_format().do_export(os.path.abspath("test.cards"))
        card.tags = set([self.database().get_or_create_tag_with_name("new_tag")])
        self.database().update_card(card)
        self.cards_format().do_export(os.path.abspath("test2.cards"))
        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"))
        _card_id, _fact_id = next(self.database().cards())
        card = self.database().card(_card_id, is_id_internal=True)
        card.grade = 2
        self.database().update_card(card)
        self.cards_format().do_import(os.path.abspath("test2.cards"))
        card = self.database().card(_card_id, is_id_internal=True)
        tag_names = [tag.name for tag in card.tags]
        assert "new_tag" in tag_names
        assert "default" in tag_names
        assert card.grade == 2

        self.cards_format().do_import("test2.cards")
        card = self.database().card(_card_id, is_id_internal=True)
        assert len(list(card.tags)) == 2
        assert card.grade == 2

    def test_cloze(self):
        fact_data = {"text": "que[sti]on"}
        card_type = self.card_type_with_id("5")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])[0]
        self.cards_format().do_export(os.path.abspath("test.cards"))
        card.tags = set([self.database().get_or_create_tag_with_name("new_tag")])
        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"))
        _card_id, _fact_id = next(self.database().cards())
        card = self.database().card(_card_id, is_id_internal=True)

    def test_media(self):
        filename_a = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", chr(0x628) + "a.ogg")
        f = open(filename_a, "w")
        print("a", file=f)
        f.close()
        os.mkdir(os.path.join(os.path.abspath("dot_test"),
        "default.db_media", "b"))
        filename_b = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", "b", chr(0x628) + "b.ogg")
        f = open(filename_b, "w")
        print("b", file=f)
        f.close()

        fact_data = {"f": "question\n<img src=\"%s\">" % (filename_a),
                     "b": "question\n<img src=\"%s\">" % (filename_b)}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])
        self.cards_format().do_export(os.path.abspath("test.cards"))

        self.database().new("import.db")
        self.cards_format().do_import(os.path.abspath("test.cards"))
        assert os.path.exists(os.path.join("dot_test", "import.db_media",
            chr(0x628) + "a.ogg"))
        assert os.path.exists(os.path.join("dot_test", "import.db_media",
            "b", chr(0x628) + "b.ogg"))

    def test_missing_media(self):
        filename_a = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", chr(0x628) + "a.ogg")
        f = open(filename_a, "w")
        print("a", file=f)
        f.close()
        os.mkdir(os.path.join(os.path.abspath("dot_test"),
        "default.db_media", "b"))
        filename_b = os.path.join(os.path.abspath("dot_test"),
            "default.db_media", "b", chr(0x628) + "b.ogg")
        f = open(filename_b, "w")
        print("b", file=f)
        f.close()

        fact_data = {"f": "question\n<img src=\"%s\">" % (filename_a),
                     "b": "question\n<img src=\"%s\">" % (filename_b)}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])

        os.remove(filename_a)
        self.cards_format().do_export(os.path.abspath("test.cards"))
        global last_error
        assert last_error.startswith("Missing")
        last_error = None

    def teardown_method(self):
        if os.path.exists(os.path.abspath("test.cards")):
            os.remove(os.path.abspath("test.cards"))
        if os.path.exists("test2.cards"):
            os.remove("test2.cards")
        MnemosyneTest.teardown_method(self)