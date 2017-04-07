#
# test_cuecard_wcu_import.py <Peter.Bienstman@UGent.be>
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
        raise NotImplementedError

    def show_warning(self, message):
        if message.startswith("media "):
            return 0
        raise NotImplementedError

class TestSmconvImport(MnemosyneTest):

    def setup(self):
        self.initialise_data_dir()
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]        
        self.mnemosyne.components.append(\
            ("test_cuecard_wcu_import", "Widget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "CuecardWcu":
                return format

    def test_1(self):
        global last_error
        filename = os.path.join(os.getcwd(), "tests", "files", "test.wcu")
        self.importer().do_import(filename)
        assert last_error is ""
        assert len([c for c in self.database().cards()]) == 4

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