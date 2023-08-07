#
# test_tsv_import.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
from pytest import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

last_error = ""

class Widget(MainWidget):

    def show_error(self, message):
        global last_error
        print(message)
        last_error = message

class TestDBImport(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("test_db_import", "Widget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()
        self.merge_db_path = os.path.join(os.getcwd(), "tests", "files", "basedir_to_merge", "to_merge.db")
        self.merge_db_tmppath = os.path.join(os.path.dirname(self.merge_db_path), "to_merge_tmp.db")
        shutil.copy2(self.merge_db_path, self.merge_db_tmppath)

    def db_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne2Db":
                return format

    def test_1(self):
        print(os.getcwd())
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_to_merge", "config.db")
        self.db_importer().do_import(filename)
        assert "configuration database" in last_error

    def test_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        old_card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["default"])[0]
        assert len([self.database().cards()]) == 1

        global last_error
        last_error = ""
        self.db_importer().do_import(self.merge_db_tmppath)
        assert last_error == ""
        db = self.database()
        assert db.con.execute("select count() from log where event_type != 26").fetchone()[0] == 258
        self.review_controller().reset()
        assert self.database().card_count() == 7
        assert self.database().active_count() == 6
        assert self.database().fact_count() == 5
        card_type = self.database().card_type("2::new clone", is_id_internal=False)
        assert self.config().card_type_property("background_colour", card_type) == 4278233600

    def teardown_method(self):
        MnemosyneTest.teardown_method(self)
        if os.path.exists(self.merge_db_path + "-journal"):
            os.remove(self.merge_db_path + "-journal")
        if os.path.exists(self.merge_db_tmppath):
            os.remove(self.merge_db_tmppath)
        if os.path.exists(self.merge_db_tmppath + "-journal"):
            os.remove(self.merge_db_tmppath + "-journal")
