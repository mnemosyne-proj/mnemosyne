#
# test_anki2_import.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil
from pytest import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class TestAnkiImport(MnemosyneTest):

    def setup_method(self):
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.initialise_data_dir()
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("test_mem_import", "Widget"))
        self.mnemosyne.components.append(\
            ("test_mem_import", "MyImportDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def anki_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Anki2":
                return format

    def _test_database(self):
        assert self.database().card_count() == 7
        assert self.database().fact_count() == 6

        card = self.database().card("1502277582871", is_id_internal=False)
        assert "img src=\"al.png\"" in card.question(render_chain="plain_text")
        assert self.config().card_type_property(\
                "font", card.card_type, "0") == \
                   "Algerian,23,-1,5,50,0,0,0,0,0,Regular"
        assert card.next_rep == 1503021600
        assert card.last_rep == card.next_rep - 3 * 86400

        card = self.database().card("1502277594395", is_id_internal=False)
        assert "audio src=\"1.mp3\"" in card.question(render_chain="plain_text")

        card = self.database().card("1502277686022", is_id_internal=False)
        assert "<$$>x</$$>&nbsp;<latex>x^2</latex>&nbsp;<$>x^3</$>" in\
                   card.question(render_chain="plain_text")

        card = self.database().card("1502797276041", is_id_internal=False)
        assert "aa <span class=cloze>[...]</span> cc" in\
                   card.question(render_chain="plain_text")
        assert "aa <span class=cloze>bbb</span> cc" in\
                   card.answer(render_chain="plain_text")

        card = self.database().card("1502797276050", is_id_internal=False)
        assert "aa bbb <span class=cloze>[...]</span>" in\
                   card.question(render_chain="plain_text")
        assert "aa bbb <span class=cloze>cc</span>" in\
                   card.answer(render_chain="plain_text")
        assert card.next_rep == -1
        assert card.last_rep == -1

        card = self.database().card("1502970432696", is_id_internal=False)
        assert "type answer" in\
                   card.question(render_chain="plain_text")
        assert "{{type:Back}}" not in\
                   card.question(render_chain="plain_text")
        assert card.next_rep == 1502970472
        assert card.last_rep == 1502970472

        card = self.database().card("1503047582690", is_id_internal=False)
        assert "subdeck card" in\
                   card.question(render_chain="plain_text")
        assert card.next_rep == -1
        assert card.last_rep == -1
        assert card.easiness == 2.5

        criterion = self.database().criterion(id=2, is_id_internal=True)
        assert criterion.data_to_string() == "(set(), {2}, set())"
        assert criterion.name == "Deck 1"
        assert len(list(self.database().criteria())) == 3

    def test_anki_1(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "anki1", "collection.anki2")
        self.anki_importer().do_import(filename)
        self.review_controller().reset()
        self._test_database()

    def test_anki_import_twice(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "anki1", "collection.anki2")
        self.anki_importer().do_import(filename)
        self.anki_importer().do_import(filename)
        self.review_controller().reset()
        self._test_database()

    def test_anki_apkg(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "anki1.apkg",)
        self.anki_importer().do_import(filename)
        self.review_controller().reset()
        self._test_database()
