#
# test_media.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

filename = ""

class Widget(MainWidget):

    def open_file_dialog(self, a, b, c):
        return filename
    
class TestMedia(MnemosyneTest):

    def restart(self):
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_media", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))

    def test_sound_1(self):
        global filename
        
        filename = ""
        self.ui_controller_main().insert_sound("")

    def test_sound_2(self):
        global filename
        
        os.system("touch a.ogg")
        filename = os.path.abspath("a.ogg")
        self.ui_controller_main().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

        filename = os.path.join(self.config().mediadir(), "a.ogg")
        self.ui_controller_main().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

    def test_img_1(self):
        global filename
        
        filename = ""
        self.ui_controller_main().insert_img("")

    def test_img_2(self):
        global filename
        
        os.system("touch a.ogg")
        filename = os.path.abspath("a.ogg")
        self.ui_controller_main().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

        filename = os.path.join(self.config().mediadir(), "a.ogg")
        self.ui_controller_main().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

    def teardown(self):
        MnemosyneTest.teardown(self)
        os.system("rm -f a.ogg")
