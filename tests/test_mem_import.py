#
# test_mem_import.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
from unittest import mock
from pytest import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.file_formats.science_log_parser import ScienceLogParser

last_error = ""

class Widget(MainWidget):

    def show_information(self, message):
        if message.startswith("Warning: "):
            return 0
        if message.startswith("No history found to import."):
            return 0
        if message.startswith("Ignoring unparsable file"):
            return 0
        if message.startswith("Upgrade from"):
            return 0
        if message.startswith("You appear"):
            return 0
        if message.startswith("Your queue is running empty, "):
            return 0
        if message.startswith("Note that"):
            return 0
        raise NotImplementedError

    def show_error(self, message):
        global last_error
        last_error = message
        if message.startswith("These cards seem to have been imported before"):
            return
        if message.startswith("Unable to open"):
            return
        if message.strip().endswith("IndexError: Mocked Error"):
            return
        print(message)
        raise Exception("Unexpected error.")


class MyImportDialog(ImportDialog):

    def activate(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_sch",
                                "default.mem")
        for format in self.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                format.do_import(filename)


class TestMemImport(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
                    asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("test_mem_import", "Widget"))
        self.mnemosyne.components.append(\
            ("test_mem_import", "MyImportDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def mem_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                return format

    @mock.patch("mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem.open",
                mock.Mock(side_effect=[FileNotFoundError,
                                       IndexError("Mocked Error")]))
    def test_exceptions(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "nothere.mem")
        self.mem_importer().do_import(filename)
        assert last_error.startswith("Unable to open")

        self.mem_importer().do_import("name_does_not_matter")
        assert last_error.strip().endswith("IndexError: Mocked Error")


    @MnemosyneTest.set_timezone_utc
    def test_card_type_1(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.mem_importer().do_import(filename)
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
        assert [tag.name for tag in card.tags] == ["__UNTAGGED__"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"

    def test_card_type_1_unseen(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided_unseen.mem")
        self.mem_importer().do_import(filename)
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
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.id == "9cff728f"
        assert "question" in card.question()
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.mem_importer().do_import(filename)
        assert last_error.startswith("These cards seem to have been imported before")

    def test_card_type_2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "2sided.mem")
        self.mem_importer().do_import(filename)
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
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided.mem")
        self.mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p_1": "p", "m_1": "t"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2

    def test_card_type_3_corrupt(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_corrupt.mem")
        self.mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "m_1": "t"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2

    def test_card_type_3_missing(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_missing.mem")
        self.mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "t", "b": "f\np"}
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1

    def test_media(self):
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.mem")
        self.mem_importer().do_import(filename)
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
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media.mem")
        self.mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2

    def test_media_missing_2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "media.mem")
        self.mem_importer().do_import(filename)
        assert not os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert not os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 0

    def test_media_slashes(self):
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs"))
        os.mkdir(os.path.join(os.getcwd(), "tests", "files", "figs", "figs"))
        figures = [\
            os.path.join(os.getcwd(), "tests", "files", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "a.png"),
            os.path.join(os.getcwd(), "tests", "files", "figs", "figs", "a.png")]
        for filename in figures:
            open(filename, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "media_slashes.mem")
        self.mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "figs", "a.png"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_media_quotes(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_media",
                                    "default.mem")
        self.mem_importer().do_import(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1

    def test_sound(self):
        os.mkdir(os.path.join(\
            os.getcwd(), "tests", "files", "soundfiles"))
        soundname = os.path.join(os.path.join(\
            os.getcwd(), "tests", "files", "soundfiles", "a.ogg"))
        open(soundname, "w")
        filename = os.path.join(os.getcwd(), "tests", "files", "sound.mem")
        self.mem_importer().do_import(filename)
        assert os.path.exists(os.path.join(\
            os.path.abspath("dot_test"), "default.db_media", "soundfiles", "a.ogg"))
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 1
        self.review_controller().reset()
        card = self.review_controller().card
        assert card.fact["f"] == """<audio src="soundfiles/a.ogg">"""

    def test_map(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "map.mem")
        self.mem_importer().do_import(filename)
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
        self.mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.review_controller().card.fact["loc"] == \
               """<b>Freistaat Th\xfcringen (Free State of Thuringia)</b>"""
        assert self.review_controller().card.tag_string() == "Germany: States, MISSING_MEDIA"

    def test_logs_new_1(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 10
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='9525224f'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='9525224f'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select scheduled_interval from log where event_type=? and object_id='9525224f'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == (6)*60*60*24
        assert self.database().con.execute(\
            """select actual_interval from log where event_type=? and object_id='9525224f'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 0 # This is an artificial log.
        timestamp = self.database().con.execute(\
            """select timestamp from log where event_type=? and object_id='9525224f'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0]
        next_rep = self.database().con.execute(\
            """select next_rep from log where event_type=? and object_id='9525224f'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0]
        assert next_rep - timestamp == (14-3)*60*60*24
        assert self.database().con.execute(\
            "select count() from log").fetchone()[0] == 25
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? order by _id desc limit 1",
            (EventTypes.LOADED_DATABASE, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? order by _id desc limit 1",
            (EventTypes.LOADED_DATABASE, )).fetchone()[0] == 7
        assert self.database().con.execute(\
            "select lapses from log where event_type=? order by _id desc limit 1",
            (EventTypes.LOADED_DATABASE, )).fetchone()[0] == 336
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? order by _id desc limit 1",
            (EventTypes.SAVED_DATABASE, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? order by _id desc limit 1",
            (EventTypes.SAVED_DATABASE, )).fetchone()[0] == 12
        assert self.database().con.execute(\
            "select lapses from log where event_type=? order by _id desc limit 1",
            (EventTypes.SAVED_DATABASE, )).fetchone()[0] == 341

    def test_logs_new_2(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_2.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='8da62cfb'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='8da62cfb'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1

    def test_logs_new_3(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_3.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 4
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='5106b621'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='5106b621'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps from log where event_type=? and object_id='5106b621'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps_since_lapse from log where event_type=? and object_id='5106b621'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1

    def test_logs_new_4(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_4.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='b7601e0c'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? and object_id='b7601e0c'",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='b7601e0c'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps from log where event_type=? and object_id='b7601e0c'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select ret_reps from log where event_type=? and object_id='b7601e0c'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps_since_lapse from log where event_type=? and object_id='b7601e0c'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1

    def test_logs_new_5(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_5.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            """select ret_reps from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            """select acq_reps_since_lapse from log where event_type=? and object_id='9c8ce28e-1a4b-4148-8287-b8a7790d86d0.1.1'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            """select object_id from log where event_type=?""",
            (EventTypes.STARTED_SCHEDULER, )).fetchone()[0] == "SM2 Mnemosyne"

    def test_logs_new_6(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "new_6.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        sql_res = self.database().con.execute(\
            "select * from log where event_type=? and object_id='4c53e29a-f9e9-498b-8beb-d3a494f61bca.1.1'",
            (EventTypes.REPETITION, )).fetchone()
        assert sql_res[4] == 5
        assert sql_res[5] == 2.5
        assert sql_res[6] == 1
        assert sql_res[7] == 0
        assert sql_res[8] == 0
        assert sql_res[9] == 1
        assert sql_res[10] == 0
        assert sql_res[11] == 0
        assert sql_res[12] == 0
        assert sql_res[14] - sql_res[2] == 345600
        assert sql_res[13] == 0
        sql_res = self.database().con.execute(\
            """select * from log where event_type=? and object_id='4c53e29a-f9e9-498b-8beb-d3a494f61bca.1.1'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()
        assert sql_res[4] == 2
        assert sql_res[5] == 2.5
        assert sql_res[6] == 1
        assert sql_res[7] == 1
        assert sql_res[8] == 0
        assert sql_res[9] == 1
        assert sql_res[10] == 1
        assert sql_res[11] == 302986
        assert sql_res[12] == 10
        assert sql_res[14] - sql_res[2] == 475774
        assert sql_res[13] == 1

    def test_logs_imported_1(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "imported_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 3
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='f5d9bbe7'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? and object_id='f5d9bbe7'",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='f5d9bbe7'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select acq_reps from log where event_type=? and object_id='f5d9bbe7'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            """select ret_reps from log where event_type=? and object_id='f5d9bbe7'
             order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 2
        assert self.database().con.execute(\
            """select acq_reps_since_lapse from log where event_type=? and object_id='f5d9bbe7'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 1

    def test_logs_imported_2(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "imported_2.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select acq_reps from log where event_type=? and object_id='14670f10'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select ret_reps from log where event_type=? and object_id='14670f10'",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select acq_reps_since_lapse from log where event_type=? and object_id='14670f10'",
            (EventTypes.REPETITION, )).fetchone()[0] == 1

    def test_logs_imported_3(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "imported_3.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1

    def test_restored_1(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "restored_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        sql_res = self.database().con.execute(\
            "select * from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()
        assert sql_res[4] == 1
        assert sql_res[5] == 2.36
        assert sql_res[6] == 23
        assert sql_res[7] == 8
        assert sql_res[8] == 2
        assert sql_res[9] == 0
        assert sql_res[10] == 0
        assert sql_res[11] == 89 * 24 * 60 * 60
        assert sql_res[12] == 0 # No last rep data.
        assert sql_res[14] - sql_res[2] == 0
        assert sql_res[13] == 5

    def test_restored_2(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "restored_2.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1

    def test_logs_act_interval(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "actinterval_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            """select actual_interval from log where event_type=? and object_id='f1300e5a'
            order by _id desc limit 1""",
            (EventTypes.REPETITION, )).fetchone()[0] == 5

    def test_logs_deleted(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "delete_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.DELETED_CARD, )).fetchone()[0] == 1

    def test_logs_corrupt_1(self): # Wrong data, missing creation event.
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "corrupt_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where object_id=?",
            ("4b59b830", )).fetchone()[0] == 3

    def test_logs_corrupt_2(self): # Wrong data, isolated deletion event.
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_1x_log_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "corrupt_2.txt")
        ScienceLogParser(self.database()).parse(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select count() from log where object_id=?",
            ("4b59b830", )).fetchone()[0] == 0

    def test_two_mem_files_sharing_same_logs(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_2_mem",
                                "deck1.mem")
        self.mem_importer().do_import(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 1
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_2_mem",
                                "deck2.mem")
        self.mem_importer().do_import(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 3
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 2
        card = self.database().card("4c8fff73", is_id_internal=False)
        assert self.database().average_thinking_time(card) == 1.5
        assert self.database().total_thinking_time(card) == 3.0
        assert self.database().card_count_for_grade(0, active_only=True) == 2
        tag = self.database().get_or_create_tag_with_name("666")
        assert self.database().card_count_for_grade_and_tag(0, tag, active_only=True) == 0
        from mnemosyne.libmnemosyne.statistics_pages.grades import Grades
        page = Grades(component_manager=self.mnemosyne.component_manager)
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tag_tree = TagTree(self.mnemosyne.component_manager, count_cards=False)
        self.nodes = self.tag_tree.nodes()
        for index, node in enumerate(self.nodes):
            if node == "666":
                page.prepare_statistics(index)
                assert page.y == [0, 0, 0, 0, 0, 0, 0]
        page.prepare_statistics(-1)
        assert page.y == [0, 2, 0, 0, 0, 0, 0]

    def test_bz2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2",
                                "default.mem")
        self.mem_importer().do_import(filename)
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 0
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.ADDED_CARD, )).fetchone()[0] == 1
        assert self.database().con.execute(\
            "select count() from log where object_id=?",
            ("82f2ed0d", )).fetchone()[0] == 0

    def test_sch(self):
        self.controller().show_import_file_dialog()
        assert self.database().card_count_scheduled_n_days_ago(0) == 1

    def test_upgrade(self):
        old_data_dir = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2")
        from mnemosyne.libmnemosyne.upgrades.upgrade1 import Upgrade1
        Upgrade1(self.mnemosyne.component_manager).upgrade_from_old_data_dir(old_data_dir)
        assert self.config()["dvipng"].rstrip() == \
               "dvipng -D 300 -T tight tmp.dvi\necho"
        assert "14pt" in self.config()["latex_preamble"]
        assert self.config()["user_id"] == "f3fb13c7"
        assert self.log().log_index_of_last_upload() == 2

        assert os.path.exists(os.path.join(old_data_dir,
            "DIRECTORY_NO_LONGER_USED_BY_MNEMOSYNE2"))
        assert os.path.exists(os.path.join(self.mnemosyne.config().data_dir,
                                           "history", "a_2.bz2"))
        log = open(os.path.join(self.mnemosyne.config().data_dir, "log.txt"))
        assert log.readline().strip() == \
               "2005-11-01 09:29:08 : Imported item 82f2ed0d 0 0 0 0 0"

    def teardown_method(self):
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
