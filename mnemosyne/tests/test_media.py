#
# test_media.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

filename = ""

class Widget(MainWidget):

    def get_filename_to_open(self, a, b, c):
        return filename
    
class TestMedia(MnemosyneTest):

    def restart(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=False)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_media", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def test_sound_1(self):
        global filename
        
        filename = ""
        self.controller().insert_sound("")

    def test_sound_2(self):
        global filename
        
        file("a.ogg", "w")
        filename = os.path.abspath("a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

        filename = os.path.join(self.database().media_dir(), "a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

    def test_sound_2_unicode(self):
        global filename
        
        file(unichr(40960) + u"a.ogg", "w")
        filename = os.path.abspath(unichr(40960) + u"a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), unichr(40960) + u"a.ogg"))

        filename = os.path.join(self.database().media_dir(), unichr(40960) + u"a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), unichr(40960) + u"a.ogg"))        
        
    def test_sound_3(self):
        global filename
        
        file("a.ogg", "w")
        
        filename = os.path.abspath("a.ogg")
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))
        
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a_1_.ogg"))
        
        self.controller().insert_sound("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a_2_.ogg"))
        
    def test_img_1(self):
        global filename
        
        filename = ""
        self.controller().insert_img("")

    def test_img_2(self):
        global filename
        
        file("a.ogg", "w")
        filename = os.path.abspath("a.ogg")
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

        filename = os.path.join(self.database().media_dir(), "a.ogg")
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

    def test_media_subdir(self):
        global filename
        
        subdir = os.path.join(self.database().media_dir(), "subdir")
        os.mkdir(subdir)
        filename = os.path.join(subdir, "b.ogg")
        os.system("touch %s" % filename)
        self.controller().insert_img("")
        assert os.path.exists(os.path.join(self.database().media_dir(),
                                           "subdir", "b.ogg"))

    def test_card(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")
        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_card_2(self):
        fact_data = {"f": "<img src=\"a.ogg>", # Missing closing "
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        assert os.path.join(self.database().media_dir(), "a.ogg") \
               not in card.question()

    def test_card_edit_none(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")

        fact_data = {"f": "edited <img src=\"%s\">" % "a.ogg",
                     "b": "answer"}
        self.controller().edit_sister_cards(card.fact, fact_data, card.card_type, 
           card_type, new_tag_names=["bla"], correspondence=None)
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()        
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_card_edit_add(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        os.system("touch b.ogg")
        full_path = os.path.abspath("b.ogg")
        fact_data = {"f": "edited <img src=\"%s\"> <img src=\"%s\">" \
                     % ("a.ogg", full_path),
                     "b": "answer"}
        self.controller().edit_sister_cards(card.fact, fact_data,
           card.card_type,  card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "b.ogg")
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()        
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2

    def test_card_edit_delete(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        fact_data = {"f": "edited ",
                     "b": "answer"}
        self.controller().edit_sister_cards(card.fact, fact_data,
           card.card_type,  card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert not os.path.exists(full_path_in_media_dir) # Autodelete.
        assert full_path_in_media_dir not in card.question()        
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.DELETED_MEDIA_FILE, )).fetchone()[0] == 1
        
    def test_card_edit_delete_used_by_other(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        fact_data = {"f": "2 <img src=\'%s\'>" % "a.ogg",
                     "b": "answer"}        
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "edited",
                     "b": "answer"}        
        self.controller().edit_sister_cards(card.fact, fact_data,
           card.card_type, card_type, new_tag_names=["bla"], correspondence=None)
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir) # Don't delete file.
        assert full_path_in_media_dir not in card.question()      
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_delete_fact(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        self.controller().delete_facts_and_their_cards([card.fact])
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert not os.path.exists(full_path_in_media_dir) # Autodelete.
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1
        
    def test_delete_fact_used_by_other(self):
        file("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, id_is_internal=True)
        fact_data = {"f": "2 <img src=\"%s\">" % "a.ogg",
                     "b": "answer"}
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        self.controller().delete_facts_and_their_cards([card.fact])
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir) # Not deleted.
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_orphaned(self):
        file(os.path.join(self.database().media_dir(), "a.ogg"), "w")
        os.mkdir(os.path.join(self.database().media_dir(), "sub"))
        file(os.path.join(self.database().media_dir(), "sub", "b.ogg"), "w")
        
        os.mkdir(os.path.join(self.database().media_dir(), "_keep"))
        file(os.path.join(self.database().media_dir(), "_keep", "b.ogg"), "w")
        
        file("c.ogg", "w")
        full_path = os.path.abspath("c.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))        
        assert os.path.exists(os.path.join(self.database().media_dir(), "sub"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "sub", "b.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep", "b.ogg"))
        
        self.database().clean_orphaned_static_media_files()
        
        assert not os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))        
        assert not os.path.exists(os.path.join(self.database().media_dir(), "sub"))
        assert not os.path.exists(os.path.join(self.database().media_dir(), "sub", "b.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "c.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep", "b.ogg"))
        
    def teardown(self):
        if os.path.exists("a.ogg"):
            os.remove("a.ogg")
        if os.path.exists("b.ogg"):
            os.remove("b.ogg")
        if os.path.exists("c.ogg"):
            os.remove("c.ogg")
        if os.path.exists(unichr(40960) + u"a.ogg"):
            os.remove(unichr(40960) + u"a.ogg")
        if os.path.exists("sub"):
            shutil.rmtree("sub")
        if os.path.exists("_keep"):
            shutil.rmtree("_keep")    
        MnemosyneTest.teardown(self)
        