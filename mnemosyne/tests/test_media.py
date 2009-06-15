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
        
    def test_sound_3(self):
        global filename
        
        os.system("touch a.ogg")
        
        filename = os.path.abspath("a.ogg")
        self.ui_controller_main().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))
        
        self.ui_controller_main().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a (1).ogg"))
        
        self.ui_controller_main().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a (2).ogg"))
        
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

    def test_media_subdir(self):
        global filename
        
        subdir = os.path.join(self.config().mediadir(), "subdir")
        os.mkdir(subdir)
        filename = os.path.join(subdir, "b.ogg")
        os.system("touch %s" % filename)
        self.ui_controller_main().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(),
                                           "subdir", "b.ogg"))

    def test_card(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])[0]
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))
        assert full_path in card.question()
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1

        # Editing, no media change
        
        # Editing, media deletion

        # Editing, media addition

        # Deleting fact

        # Deleting fact with another fact using the same file

    def test_card_2(self):
        fact_data = {"q": "<img src=\"a.ogg>", # Missing closing "
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])[0]
        assert os.path.join(self.config().mediadir(), "a.ogg") \
               not in card.question()
        
    def teardown(self):
        os.system("rm -f a.ogg")
        MnemosyneTest.teardown(self)
        
