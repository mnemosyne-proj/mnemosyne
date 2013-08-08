#
# test_tsv_import.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

last_error = ""

class Widget(MainWidget):

    def activate(self):
        self.review_controller().reset()

    def show_error(self, message):
        global last_error
        last_error = message
        if message.startswith("Could not load "):
            return 0
        if message.startswith("Could not determine"):
            return 0
        if message.startswith("Badly formed input"):
            return 0
        raise NotImplementedError

    def show_warning(self, message):
        if message.startswith("media "):
            return 0
        raise NotImplementedError

class TestTsvImport(MnemosyneTest):

    def setup(self):
        shutil.rmtree("dot_test", ignore_errors=True)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.components.append(\
            ("test_tsv_import", "Widget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def tsv_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Tsv":
                return format

    def test_file_not_found(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "nothere.tsv")
        self.tsv_importer().do_import(filename)
        assert last_error.startswith("Could not load")
        last_error = ""

    def test_1(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_1.txt")
        self.tsv_importer().do_import(filename)
        assert last_error == ""
        self.review_controller().reset()
        assert self.database().card_count() == 3

    def test_2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_2.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        print last_error
        assert last_error == ""
        self.review_controller().reset()
        assert self.database().card_count() == 2
        assert unichr(33267) in self.review_controller().card.answer()

    def test_3(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_3.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert last_error.startswith("Badly formed input")
        last_error = ""

    def test_4(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "word_import.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert self.database().card_count() == 5
        assert last_error == ""

    def test_5(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "excel_import.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert self.database().card_count() == 5
        assert last_error == ""

    def test_6(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_4.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert self.database().card_count() == 1
        self.review_controller().reset()
        assert u"\u00E0" in self.review_controller().card.question()
        assert last_error == ""

    def test_7(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_5.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert self.database().card_count() == 1
        self.review_controller().reset()
        assert u"\u00E0" in self.review_controller().card.question()
        assert last_error == ""

    def test_8(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_6.txt")
        self.tsv_importer().do_import(filename, 'extra_tag_name')
        assert self.database().card_count() == 2
        self.review_controller().reset()
        assert  self.review_controller().card.fact["n"] == "notes"
        assert last_error == ""

    def test_media(self):
        global last_error
        file(os.path.join(os.getcwd(), "dot_test", "default.db_media", "a.png"), "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "tsv_media.txt")
        self.tsv_importer().do_import(filename)
        assert self.database().card_count() == 2
        assert self.database().card_count_for_tags(\
            [self.database().get_or_create_tag_with_name("MISSING_MEDIA")], False) == 1
        assert last_error == ""
        fact_data = {"f": "question",
                     "b": ""}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(\
            fact_data, card_type, grade=-1, tag_names=["default"])[0]
        self.tsv_importer().do_export(os.path.join(os.getcwd(), "dot_test", "test.txt"))


    def teardown(self):
        filename = \
            os.path.join(os.getcwd(), "dot_test", "default.db_media", "a.png")
        if os.path.exists(filename):
            os.remove(filename)
        filename = \
            os.path.join(os.getcwd(), "dot_test", "test.txt")
        if os.path.exists(filename):
            os.remove(filename)
        MnemosyneTest.teardown(self)