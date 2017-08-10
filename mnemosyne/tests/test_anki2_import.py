#
# test_anki2_import.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

last_error = ""

class Widget(MainWidget):

    def show_information(self, message):
        raise NotImplementedError

    def show_error(self, message):
        global last_error
        last_error = message
        #if message.startswith("Unable to open"):
        #    return
        raise NotImplementedError


class TestAnkiImport(MnemosyneTest):

    def setup(self):
        sys.path.append(os.path.join(\
            os.getcwd(), "..", "mnemosyne", "libmnemosyne", "renderers"))
        self.initialise_data_dir()
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.translators.gettext_translator", "GetTextTranslator"))
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

    def test_anki_1(self):
        filename = os.path.join(os.getcwd(), "files", "anki1", "collection.anki2")
        self.anki_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 3

        card = self.database().card("1502277582871", is_id_internal=False)
        assert "img src=\"al.png\"" in card.question(render_chain="plain_text")

        card = self.database().card("1502277594395", is_id_internal=False)
        assert "audio src=\"1.mp3\"" in card.question(render_chain="plain_text")

        card = self.database().card("1502277686022", is_id_internal=False)
        assert "<$$>x</$$>&nbsp;<latex>x^2</latex>&nbsp;<$>x^3</$>" in\
               card.question(render_chain="plain_text")
