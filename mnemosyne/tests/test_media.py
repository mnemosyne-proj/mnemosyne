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
        self.review_controller().reset()

    def test_sound_1(self):
        global filename
        
        filename = ""
        self.controller().insert_sound("")

    def test_sound_2(self):
        global filename
        
        os.system("touch a.ogg")
        filename = os.path.abspath("a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

        filename = os.path.join(self.config().mediadir(), "a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))
        
    def test_sound_3(self):
        global filename
        
        os.system("touch a.ogg")
        
        filename = os.path.abspath("a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))
        
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a (1).ogg"))
        
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a (2).ogg"))
        
    def test_img_1(self):
        global filename
        
        filename = ""
        self.controller().insert_img("")

    def test_img_2(self):
        global filename
        
        os.system("touch a.ogg")
        filename = os.path.abspath("a.ogg")
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

        filename = os.path.join(self.config().mediadir(), "a.ogg")
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(), "a.ogg"))

    def test_media_subdir(self):
        global filename
        
        subdir = os.path.join(self.config().mediadir(), "subdir")
        os.mkdir(subdir)
        filename = os.path.join(subdir, "b.ogg")
        os.system("touch %s" % filename)
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.config().mediadir(),
                                           "subdir", "b.ogg"))

    def test_card(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["q"]
        assert full_path_in_media_dir not in card.fact.data["q"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1

    def test_card_2(self):
        fact_data = {"q": "<img src=\"a.ogg>", # Missing closing "
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        assert os.path.join(self.config().mediadir(), "a.ogg") \
               not in card.question()

    def test_card_edit_none(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")

        fact_data = {"q": "edited <img src=\"%s\">" % "a.ogg",
                     "a": "answer"}
        self.controller().update_related_cards(card.fact, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)

        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["q"]
        assert full_path_in_media_dir not in card.fact.data["q"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()        
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1

    def test_card_edit_add(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]

        os.system("touch b.ogg")
        full_path = os.path.abspath("b.ogg")
        fact_data = {"q": "edited <img src=\"%s\"> <img src=\"%s\">" \
                     % ("a.ogg", full_path),
                     "a": "answer"}
        self.controller().update_related_cards(card.fact, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "b.ogg")
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["q"]
        assert full_path_in_media_dir not in card.fact.data["q"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()        
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 2

    def test_card_edit_delete(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "edited ",
                     "a": "answer"}
        self.controller().update_related_cards(card.fact, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")
        assert not os.path.exists(full_path_in_media_dir)
        assert full_path_in_media_dir not in card.question()        
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().DELETED_MEDIA, )).fetchone()[0] == 1
        
    def test_card_edit_delete_used_by_other(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2 <img src=\"%s\">" % "a.ogg",
                     "a": "answer"}
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "edited",
                     "a": "answer"}        
        self.controller().update_related_cards(card.fact, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir) # Don't delete file.
        assert full_path_in_media_dir not in card.question()      
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().DELETED_MEDIA, )).fetchone()[0] == 1

    def test_delete_fact(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        self.database().delete_fact_and_related_data(card.fact)
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")
        assert not os.path.exists(full_path_in_media_dir)
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().DELETED_MEDIA, )).fetchone()[0] == 1
        
    def test_delete_fact_used_by_other(self):
        os.system("touch a.ogg")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"q": "<img src=\"%s\">" % full_path,
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"q": "2 <img src=\"%s\">" % "a.ogg",
                     "a": "answer"}
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        self.database().delete_fact_and_related_data(card.fact)
        full_path_in_media_dir = os.path.join(self.config().mediadir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir) # Not deleted.
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().DELETED_MEDIA, )).fetchone()[0] == 1
        
    def teardown(self):
        os.system("rm -f a.ogg")
        os.system("rm -f b.ogg")
        MnemosyneTest.teardown(self)
        
