#
# test_mem_import.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class SeenBeforeError(Exception):
    pass

class FileNotFoundError(Exception):
    pass

class Widget(MainWidget):

    def information_box(self, message):
        if message.startswith("Missing media file"):
            return 0
        raise NotImplementedError

    def error_box(self, message):
        if message.startswith("This file seems to have been imported before"):
            raise SeenBeforeError
        if message.startswith("Unable to open"):
            raise FileNotFoundError
        raise NotImplementedError        


class TestMemImport(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))        
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_mem_import", "Widget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))
        self.review_controller().reset()
        
    def get_mem_importer(self):
        for format in self.mnemosyne.component_manager.get_all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                return format

    @raises(FileNotFoundError)
    def test_file_not_found(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "nothere.mem")
        self.get_mem_importer().do_import(filename)
        
    def test_card_type_1(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.grade == 2
        assert card.easiness == 2.5
        assert card.acq_reps == 1
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 1
        assert card.ret_reps_since_lapse == 0
        assert [tag.name for tag in card.tags] == ["<default>"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"
        
    def test_card_type_1_unseen(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided_unseen.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.grade == -1
        assert card.easiness == 2.5
        assert card.acq_reps == 0
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 0
        assert card.ret_reps_since_lapse == 0
        assert card.last_rep == -1
        assert card.next_rep == -1
        
    @raises(SeenBeforeError)
    def test_card_type_1_updated(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.id == "9cff728f"
        assert "question" in card.question()
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.get_mem_importer().do_import(filename)      
        
    def test_card_type_2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "2sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert "question" in card_1.question()
        assert "answer" in card_1.answer()        
        cards = self.database().cards_from_fact(card_1.fact)
        if cards[0] == card_1:
            card_2 = cards[1]
        else:
            card_2 = cards[0]
        assert "question" in card_2.answer()
        assert "answer" in card_2.question()
        
    def test_card_type_3(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p": "p", "t": "t"}

    def test_card_type_3_corrupt(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_corrupt.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p": "", "t": "t"}
        
    def test_card_type_3_missing(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_missing.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card_1 = self.review_controller().card
        print card_1.fact.data
        assert card_1.fact.data == {"q": "t", "a": "f\np"}

    def test_media(self):
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))       
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            file(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.mem")
        self.get_mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 3
        for filename in figures:
            os.remove(filename)
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs"))        

    def test_media_missing(self):
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))       
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png")]
        for filename in figures:
            file(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.mem")
        self.get_mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 2
        for filename in figures:
            os.remove(filename)
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs"))        

    def test_media_slashes(self):
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))       
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            file(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media_slashes.mem")
        self.get_mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 3
        for filename in figures:
            os.remove(filename)
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        os.rmdir(os.path.join(os.getcwd(), "tests", "files", "figs"))  

    def test_sound(self):
        soundname = os.path.join(os.path.join(\
            os.getcwd(), "tests", "files", "a.ogg"))
        file(soundname, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "sound.mem")
        self.get_mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.ogg"))
        assert self.database().con.execute(\
            "select count() from history where event=?",
            (self.log().ADDED_MEDIA, )).fetchone()[0] == 1
        self.review_controller().reset()
        card = self.review_controller().card
        assert card.fact["q"] == """<audio src="a.ogg">"""
        os.remove(soundname)

    def test_map(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "map.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card = self.review_controller().card
        assert card.fact["loc"] == "<b>Drenthe</b>"
        assert card.fact["marked"] == \
          """<img src_missing="maps/Netherlands-Provinces/Drenthe.png">"""
        assert card.fact["blank"] == \
          """<img src_missing="maps/Netherlands-Provinces/Netherlands-Provinces.png">"""
        
    def test_dups(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "dups.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.review_controller().card.fact["loc"] == \
               u"""<b>Freistaat Th\xfcringen (Free State of Thuringia)</b>"""
        assert self.review_controller().card.tag_string() == "Germany: States"
        
        
