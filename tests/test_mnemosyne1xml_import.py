#
# test_mnemosyne1xml_import.py <Johannes.Baiter@gmail.com>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

last_error = ""
answer = None

class Widget(MainWidget):

    def show_information(self, message):
        if message.startswith("Warning: "):
            return 0
        if message.startswith("Ignoring unparsable file"):
            return 0
        if message.startswith("You appear"):
            return 0
        if message.startswith("Your queue is running empty, "):
            return 0
        raise NotImplementedError

    def show_error(self, message):
        global last_error
        last_error = message
        if message.startswith("These cards seem to have been imported before"):
            return
        if message.startswith("Unable to open"):
            return
        if message.startswith("Unable to parse"):
            return
        if message.startswith("Bad file version:"):
            return
        if message.startswith("XML file does not seem"):
            return
        raise NotImplementedError

    def show_question(self, question, option0, option1, option2):
        return answer


class TestMnemosyne1XMLImport(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("test_mnemosyne1xml_import", "Widget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def xml_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1XML":
                return format

    def test_file_not_found(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "nothere.xml")
        self.xml_importer().do_import(filename)
        assert last_error.startswith("Unable to open")

    def test_wrong_format(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "wrong_format.xml")
        self.xml_importer().do_import(filename)
        assert last_error.startswith("Unable to parse")

    def test_bad_version(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "bad_version.xml")
        self.xml_importer().do_import(filename)
        assert last_error.startswith("XML file does not seem")

    @MnemosyneTest.set_timezone_utc
    def test_card_type_1(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 4
        card = self.review_controller().card
        assert card.grade == 2
        assert card.easiness == 2.5
        assert card.acq_reps == 1
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 1
        assert card.ret_reps_since_lapse == 0
        assert [tag.name for tag in card.tags] == ["__UNTAGGED__"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"

    def test_card_type_1_abort(self):
        global answer
        answer = 1
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 0

    def test_card_type_1_unseen(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided_unseen.xml")
        self.xml_importer().do_import(filename)
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
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1

    def test_card_type_1_edited(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 4
        card = self.review_controller().card
        assert card.id == "9cff728f"
        assert "question" in card.question()
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.xml")
        self.xml_importer().do_import(filename)
        assert last_error.startswith("These cards seem to have been imported before")

    def test_card_type_2(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "2sided.xml")
        self.xml_importer().do_import(filename)
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
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2

    def test_card_type_3(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p_1": "p", "m_1": "t"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2

    def test_card_type_3_corrupt(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_corrupt.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "m_1": "t"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2

    def test_card_type_3_missing(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_missing.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "t", "b": "f\np"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1

    def test_media(self):
        global answer
        answer = 0
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.xml")
        self.xml_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_media_missing(self):
        global answer
        answer = 0
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.xml")
        self.xml_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2

    def test_media_missing_2(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "media.xml")
        self.xml_importer().do_import(filename)
        assert not os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert not os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 0

    def test_media_slashes(self):
        global answer
        answer = 0
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media_slashes.xml")
        self.xml_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_sound(self):
        global answer
        answer = 0
        os.mkdir(os.path.join(\
            os.getcwd(), "tests", "files", "soundfiles"))
        soundname = os.path.join(os.path.join(\
            os.getcwd(), "tests", "files", "soundfiles", "a.ogg"))
        open(soundname, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "sound.xml")
        self.xml_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "soundfiles", "a.ogg"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1
        self.review_controller().reset()
        card = self.review_controller().card
        assert card.fact["f"] == """<audio src="soundfiles/a.ogg">"""

    def test_map(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "map.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card = self.review_controller().card
        assert card.fact["loc"] == "<b>Drenthe</b>"
        assert card.fact["marked"] == \
          """<img src_missing="maps/Netherlands-Provinces/Drenthe.png">"""
        assert card.fact["blank"] == \
          """<img src_missing="maps/Netherlands-Provinces/Netherlands-Provinces.png">"""

    def test_dups(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "dups.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        assert self.review_controller().card.fact["loc"] == \
               """<b>Freistaat Th\xfcringen (Free State of Thuringia)</b>"""
        assert self.review_controller().card.tag_string() == "Germany: States, MISSING_MEDIA"

    def test_anon_id(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "anon_id.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        fact = self.review_controller().card.fact
        for card in self.database().cards_from_fact(fact):
            assert not card.id.startswith("_")
        assert self.database().card_count() == 2

    def test_anon_id_2(self):
        global answer, last_error
        answer = 0
        last_error = None
        filename = os.path.join(os.getcwd(), "tests", "files", "anon_id.xml")
        self.xml_importer().do_import(filename)
        assert last_error == None
        self.xml_importer().do_import(filename)
        assert last_error == None
        self.review_controller().reset()
        fact = self.review_controller().card.fact
        for card in self.database().cards_from_fact(fact):
            assert not card.id.startswith("_")
        assert self.database().card_count() == 4

    def test_no_id(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "no_id.xml")
        self.xml_importer().do_import(filename)
        self.review_controller().reset()
        fact = self.review_controller().card.fact
        for card in self.database().cards_from_fact(fact):
            assert card.id

    def test_bad_xml(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "bad_xml.xml")
        self.xml_importer().do_import(filename)
        assert last_error.startswith("Unable to parse")

    def test_tags(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "tag.xml")
        self.xml_importer().do_import(filename, extra_tag_names="extra")
        self.review_controller().reset()
        assert len(self.review_controller().card.tags) == 2

    def test_log(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "sound.xml")
        self.xml_importer().do_import(filename)
        ids = [cursor[0] for cursor in self.database().con.execute(\
            "select distinct object_id from log where event_type='6' or event_type='7'")]
        assert ids == ['ef2e21e1']

    def teardown_method(self):
        global answer
        answer = 0
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2",
                                    "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2")
        if os.path.exists(filename):
            os.remove(filename)
        filename = os.path.join(os.getcwd(), "tests", "files", "a.png")
        if os.path.exists(filename):
            os.remove(filename)
        filename = os.path.join(os.getcwd(), "tests", "files", "a.ogg")
        if os.path.exists(filename):
            os.remove(filename)
        dirname = os.path.join(os.getcwd(), "tests", "files", "figs")
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        dirname = os.path.join(os.getcwd(), "tests", "files", "soundfiles")
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        MnemosyneTest.teardown_method(self)
