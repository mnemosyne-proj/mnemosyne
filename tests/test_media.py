#
# test_media.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

filename = ""
answer = 0

class Widget(MainWidget):

    def get_filename_to_open(self, a, b, c):
        return filename

    def show_question(self, question, option0, option1, option2):
        if question.startswith("Found unused"):
            return answer
        else:
            raise NotImplementedError

class TestMedia(MnemosyneTest):

    def restart(self):
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_media", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def test_sound_1(self):
        global filename

        filename = ""
        self.controller().show_insert_sound_dialog("")

    def test_sound_2(self):
        global filename

        open("a.ogg", "w")
        filename = os.path.abspath("a.ogg")
        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

        filename = os.path.join(self.database().media_dir(), "a.ogg")
        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

    def test_sound_2_unicode(self):
        global filename

        open(chr(40960) + "a.ogg", "w")
        filename = os.path.abspath(chr(40960) + "a.ogg")
        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), chr(40960) + "a.ogg"))

        filename = os.path.join(self.database().media_dir(), chr(40960) + "a.ogg")
        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), chr(40960) + "a.ogg"))

    def test_sound_3(self):
        global filename

        open("a.ogg", "w")

        filename = os.path.abspath("a.ogg")
        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a_1.ogg"))

        self.controller().show_insert_sound_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a_2.ogg"))

    def test_img_1(self):
        global filename

        filename = ""
        self.controller().show_insert_img_dialog("")

    def test_img_2(self):
        global filename

        open("a.ogg", "w")
        filename = os.path.abspath("a.ogg")
        self.controller().show_insert_img_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

        filename = os.path.join(self.database().media_dir(), "a.ogg")
        self.controller().show_insert_img_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))

    def test_media_subdir(self):
        global filename

        subdir = os.path.join(self.database().media_dir(), "subdir")
        os.mkdir(subdir)
        filename = os.path.join(subdir, "b.ogg")
        open(filename, "w")
        self.controller().show_insert_img_dialog("")
        assert os.path.exists(os.path.join(self.database().media_dir(),
                                           "subdir", "b.ogg"))

    def test_card(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg").replace("\\", "/")
        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = \
            os.path.join(self.database().media_dir(), "a.ogg").replace("\\", "/")
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_audio_start_stop(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg").replace("\\", "/")
        fact_data = {"f": "<audio src=\"%s\" start=\"1\" stop=\"3\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = \
            os.path.join(self.database().media_dir(), "a.ogg").replace("\\", "/")
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path.replace(" ", "%20") not in card.question()
        assert full_path_in_media_dir.replace(" ", "%20") in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_external_media(self):
        fact_data = {"f": "<img src=\"http://www.chine-nouvelle.com/jdd/public/ct/pinyinaudio/shu4.mp3\"",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        assert "http" in card.question()
        assert "file" not in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 0

    def test_card_2(self):
        fact_data = {"f": "<img src=\"a.ogg>", # Missing closing "
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        assert os.path.join(self.database().media_dir(), "a.ogg") \
               not in card.question()

    def test_missing_media(self):
        fact_data = {"f": "<img src=\"missing.ogg\">",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        assert "src_missing" in card.question()

    def test_long_media(self):
        filename = 220*"a"
        fact_data = {"f": "<img src=\"%s\">" % (filename, ),
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]

    def test_card_edit_none(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        full_path_in_media_dir = \
            os.path.join(self.database().media_dir(), "a.ogg").replace("\\", "/")

        fact_data = {"f": "edited <img src=\"%s\">" % "a.ogg",
                     "b": "answer"}
        self.controller().edit_card_and_sisters(card, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_card_edit_add(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg").replace("\\", "/")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        open("b.ogg", "w")
        full_path = os.path.abspath("b.ogg").replace("\\", "/")
        fact_data = {"f": "edited <img src=\"%s\"> <img src=\"%s\">" \
                     % ("a.ogg", full_path),
                     "b": "answer"}
        self.controller().edit_card_and_sisters(card, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        card = self.database().card(card._id, is_id_internal=True)
        full_path_in_media_dir = \
            os.path.join(self.database().media_dir(), "b.ogg").replace("\\", "/")
        assert os.path.exists(full_path_in_media_dir)
        assert full_path not in card.fact.data["f"]
        assert full_path_in_media_dir not in card.fact.data["f"]
        assert full_path not in card.question()
        assert full_path_in_media_dir in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2

    def test_card_edit_delete(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg").replace("\\", "/")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        fact_data = {"f": "edited ",
                     "b": "answer"}
        self.controller().edit_card_and_sisters(card, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        full_path_in_media_dir = \
            os.path.join(self.database().media_dir(), "a.ogg").replace("\\", "/")
        self.database().delete_unused_media_files(self.database().unused_media_files())
        assert not os.path.exists(full_path_in_media_dir)
        assert full_path_in_media_dir not in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.DELETED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_card_edit_delete_used_by_other(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        fact_data = {"f": "2 <img src=\'%s\'>" % "a.ogg",
                     "b": "answer"}
        self.controller().create_new_cards(fact_data, card_type,
                                           grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "edited",
                     "b": "answer"}
        self.controller().edit_card_and_sisters(card, fact_data,
           card_type, new_tag_names=["bla"], correspondence=None)
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert os.path.exists(full_path_in_media_dir) # Don't delete file.
        assert full_path_in_media_dir not in card.question()
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_delete_fact(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
        self.controller().delete_facts_and_their_cards([card.fact])
        self.database().delete_unused_media_files(self.database().unused_media_files())
        full_path_in_media_dir = os.path.join(self.database().media_dir(), "a.ogg")
        assert not os.path.exists(full_path_in_media_dir) # Autodelete.
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_delete_fact_used_by_other(self):
        open("a.ogg", "w")
        full_path = os.path.abspath("a.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        # Make sure we don't reuse existing objects.
        card = self.database().card(card._id, is_id_internal=True)
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

    def test_unused(self):
        open(os.path.join(self.database().media_dir(), "a.ogg"), "w")
        os.mkdir(os.path.join(self.database().media_dir(), "sub"))
        open(os.path.join(self.database().media_dir(), "sub", "b.ogg"), "w")

        os.mkdir(os.path.join(self.database().media_dir(), "_keep"))
        open(os.path.join(self.database().media_dir(), "_keep", "b.ogg"), "w")

        open("c.ogg", "w")
        full_path = os.path.abspath("c.ogg")

        fact_data = {"f": "<img src=\"%s\">" % full_path,
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]

        assert os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "sub"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "sub", "b.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep", "b.ogg"))

        self.database().delete_unused_media_files(self.database().unused_media_files())

        assert not os.path.exists(os.path.join(self.database().media_dir(), "a.ogg"))
        assert not os.path.exists(os.path.join(self.database().media_dir(), "sub"))
        assert not os.path.exists(os.path.join(self.database().media_dir(), "sub", "b.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "c.ogg"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep"))
        assert os.path.exists(os.path.join(self.database().media_dir(), "_keep", "b.ogg"))

    def test_unused_latex(self):
        fact_data = {"f": "<latex>a</latex>",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        card.question()
        latex_dir = os.path.join(self.database().media_dir(), "_latex")
        assert os.path.exists(latex_dir)
        self.database().delete_unused_media_files(self.database().unused_media_files())
        assert not os.path.exists(latex_dir)

    def test_database_not_in_datadir(self):
        assert "dot_test" in self.database().media_dir()
        self.database().new(os.path.abspath("outside.db"))
        assert self.database().media_dir() == os.path.join(\
            os.path.dirname(os.path.abspath("outside.db")), "outside.db_media").replace("\\", "/")
        assert "dot_test" not in self.database().media_dir()

    def teardown_method(self):
        MnemosyneTest.teardown_method(self)
        if os.path.exists("a.ogg"):
            os.remove("a.ogg")
        if os.path.exists("b.ogg"):
            os.remove("b.ogg")
        if os.path.exists("c.ogg"):
            os.remove("c.ogg")
        if os.path.exists(chr(40960) + "a.ogg"):
            os.remove(chr(40960) + "a.ogg")
        if os.path.exists("sub"):
            shutil.rmtree("sub")
        if os.path.exists("_keep"):
            shutil.rmtree("_keep")
        if os.path.exists("outside.db"):
            os.remove("outside.db")
        if os.path.exists("outside.db-journal"):
            os.remove("outside.db-journal")
