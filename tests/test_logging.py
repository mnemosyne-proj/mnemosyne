#
# test_logging.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
import time

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MyMainWidget(MainWidget):

    def show_question(self, question, b, c, d):
        if question == "Delete this card?":
            return 1 # Yes
        else:
            raise NotImplementedError


class TestLogging(MnemosyneTest):

    def restart(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)

    def test_logging(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        card_id_1 = card.id
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(1)
        self.review_controller().grade_answer(4)

        self.mnemosyne.finalise()
        self.restart()
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "2", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        self.controller().delete_current_card()

        self.log().dump_to_science_log()

        sql_res = self.database().con.execute(\
            "select * from log where _id=1").fetchone()
        assert sql_res[1] == EventTypes.STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=2").fetchone()
        assert sql_res[1] == EventTypes.STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from log where _id=3").fetchone()
        assert sql_res[1] == EventTypes.LOADED_DATABASE
        assert sql_res[6] == 0
        assert sql_res[7] == 0
        assert sql_res[8] == 0

        sql_res = self.database().con.execute(\
            "select * from log where _id=11").fetchone()
        assert sql_res[1] == EventTypes.ADDED_TAG
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=12").fetchone()
        assert sql_res[1] == EventTypes.EDITED_CRITERION
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=13").fetchone()
        assert sql_res[1] == EventTypes.ADDED_FACT
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=14").fetchone()
        assert sql_res[1] == EventTypes.ADDED_CARD
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=15").fetchone()
        assert sql_res[1] == EventTypes.REPETITION
        assert sql_res[6] == 1
        assert sql_res[7] == 0
        assert sql_res[11] == 0
        assert sql_res[12] == 0
        assert sql_res[14] - sql_res[2] == 0
        assert sql_res[13] == 0
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=16").fetchone()
        assert sql_res[1] == EventTypes.REPETITION
        assert sql_res[6] == 2
        assert sql_res[7] == 0
        assert sql_res[11] == 0
        assert sql_res[12] <= 10 # Depends on CPU load.
        assert sql_res[14] - sql_res[2] == 0
        assert sql_res[13] == 0

        sql_res = self.database().con.execute(\
            "select * from log where _id=17").fetchone()
        assert sql_res[1] == EventTypes.REPETITION
        assert sql_res[6] == 3
        assert sql_res[7] == 0
        assert sql_res[11] == 0
        assert sql_res[12] <= 10 # Depends on CPU load.
        new_interval = sql_res[14] - sql_res[2]
        assert new_interval > 0
        assert sql_res[13] == 0

        sql_res = self.database().con.execute(\
            "select * from log where _id=18").fetchone()
        assert sql_res[1] == EventTypes.SAVED_DATABASE
        assert sql_res[6] == 0
        assert sql_res[7] == 0
        assert sql_res[8] == 1

        sql_res = self.database().con.execute(\
            "select * from log where _id=19").fetchone()
        assert sql_res[1] == EventTypes.STOPPED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=20").fetchone()
        assert sql_res[1] == EventTypes.STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=21").fetchone()
        assert sql_res[1] == EventTypes.STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from log where _id=22").fetchone()
        assert sql_res[1] == EventTypes.LOADED_DATABASE
        assert sql_res[6] == 0
        assert sql_res[7] == 0
        assert sql_res[8] == 1

        sql_res = self.database().con.execute(\
            "select * from log where _id=30").fetchone()
        assert sql_res[1] == EventTypes.ADDED_FACT
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=31").fetchone()
        assert sql_res[1] == EventTypes.ADDED_CARD

        sql_res = self.database().con.execute(\
            "select * from log where _id=32").fetchone()
        assert sql_res[1] == EventTypes.DELETED_CARD
        assert sql_res[3] is not None

        sql_res = self.database().con.execute(\
            "select * from log where _id=33").fetchone()
        assert sql_res[1] == EventTypes.DELETED_FACT
        assert sql_res[3] is not None

        self.config()["upload_science_logs"] = True
        self.database().dump_to_science_log()

        logfile = os.path.join(os.path.abspath("dot_test"), "log.txt")
        found = False
        for line in open(logfile):
            if "R " + card_id_1 + " 4" in line:
                found = True
                assert str(new_interval) + " 0 | 0.0" in line
        assert found == True

    def test_unique_index(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_2 = self.card_type_with_id("2")
        card_1, card_2 = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        log_index = self.database().con.execute(\
            """select _id from log order by _id desc limit 1""").fetchone()[0]
        # Note: we need to keep the last log entry intact, otherwise indexes
        # start again at 1 and mess up the sync.
        self.database().con.execute("""delete from log where _id <?""", (log_index,))
        self.database().save()
        self.database().con.execute("""vacuum""")
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_2 = self.card_type_with_id("1")
        card_1  = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        assert self.database().con.execute(\
            """select _id from log order by _id limit 1""").fetchone()[0] \
            == log_index

    def test_recover_user_id(self):
        assert self.config()["user_id"] is not None
        MnemosyneTest.teardown_method(self)

        open(os.path.join(os.getcwd(), "dot_test", "history", "userid_001.bz2"), "w")
        os.remove(os.path.join(os.getcwd(), "dot_test", "config.db"))

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()

        assert self.config()["user_id"] == "userid"

    def test_recover_user_id_2(self):
        assert self.config()["user_id"] is not None
        MnemosyneTest.teardown_method(self)

        open(os.path.join(os.getcwd(), "dot_test", "history", "userid_machine_001.bz2"), "w")
        os.remove(os.path.join(os.getcwd(), "dot_test", "config.db"))

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()

        assert self.config()["user_id"] == "userid"

    def test_log_index_of_last_upload_1(self):
        assert self.log().log_index_of_last_upload() == 0

    def test_log_index_of_last_upload_2(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2", "user_%s_2.bz2" % machine_id]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2

    def test_log_index_of_last_upload_3(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2"]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 1

    def test_log_index_of_last_upload_4(self):
        machine_id = self.config().machine_id()
        for filename in ["user_005.bz2"]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 5

    def test_log_index_of_last_upload_5(self):
        machine_id = self.config().machine_id()
        for filename in ["user_othermachine_005.bz2"]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 0

    def test_log_index_of_last_upload_6(self):
        machine_id = self.config().machine_id()
        for filename in ["user_othermachine_005.bz2", "user_%s_2.bz2" % machine_id]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2

    def test_log_index_of_last_upload_7(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2", "user_othermachine_005.bz2", "user_%s_2.bz2" % machine_id]:
            open(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2

    def test_log_upload(self):
        machine_id_file = os.path.join(self.mnemosyne.config().config_dir, "machine.id")
        f = open(machine_id_file, "w")
        print("TESTMACHINE", file=f)
        f.close()
        self.config().change_user_id("UPLOADTEST")
        self.config()["max_log_size_before_upload"] = 1
        MnemosyneTest.teardown_method(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()
        MnemosyneTest.teardown_method(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()
        MnemosyneTest.teardown_method(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()


    def test_log_upload_bad_server(self):
        # Most reliable way of setting this variable is throug config.py, otherwise
        # it will stay alive in a dangling imported userconfig.
        config_py_file = os.path.join(self.mnemosyne.config().config_dir, "config.py")
        f = open(config_py_file, "w")
        print("science_server = \"noserver:80\"", file=f)
        f.close()

        machine_id_file = os.path.join(self.mnemosyne.config().config_dir, "machine.id")
        f = open(machine_id_file, "w")
        print("TESTMACHINE", file=f)
        f.close()
        self.config().change_user_id("UPLOADTEST")
        self.config()["max_log_size_before_upload"] = 1
        MnemosyneTest.teardown_method(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()
        MnemosyneTest.teardown_method(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()

    def mem_importer(self):
        for format in self.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                return format

    def test_archive_old_logs(self):
        # Import old history.
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2",
                                "default.mem")
        self.mem_importer().do_import(filename)
        assert self.database().con.execute("select count() from log").fetchone()[0] == 23
        assert not os.path.exists(os.path.join("dot_test", "archive"))
        # Archive.
        self.database().archive_old_logs()
        assert self.database().con.execute("select count() from log").fetchone()[0] == 12
        archive_name = os.listdir(os.path.join(os.getcwd(), "dot_test", "archive"))[0]
        archive_path = os.path.join(os.getcwd(), "dot_test", "archive", archive_name)
        import sqlite3
        arch_con = sqlite3.connect(archive_path)
        assert arch_con.execute("select count() from log").fetchone()[0] == 11

    def test_log_warn_about_too_many_cards(self):
        timestamp = int(time.time())
        self.database().log_warn_about_too_many_cards(timestamp)
        results = self.database().con.execute("""select timestamp from log WHERE event_type=? and timestamp = ?""", (EventTypes.WARNED_TOO_MANY_CARDS, timestamp)).fetchall()
        assert 1 == len(results)
