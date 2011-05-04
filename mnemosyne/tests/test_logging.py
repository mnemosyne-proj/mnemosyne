#
# test_logging.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MyMainWidget(MainWidget):

    def show_question(self, question, b, c, d):
        if question == "Delete this card?":
            return 0 # Yes
        else:
            raise NotImplementedError
            

class TestLogging(MnemosyneTest):
    
    def restart(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()
        
    def test_logging(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
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
        assert sql_res["event_type"] == EventTypes.STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=2").fetchone()
        assert sql_res["event_type"] == EventTypes.STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from log where _id=3").fetchone()
        assert sql_res["event_type"] == EventTypes.LOADED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 0

        sql_res = self.database().con.execute(\
            "select * from log where _id=4").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_TAG
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=5").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_FACT
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=6").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_CARD
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=7").fetchone()
        assert sql_res["event_type"] == EventTypes.REPETITION
        assert sql_res["acq_reps"] == 1
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] == 0
        assert sql_res["new_interval"] == 0
        assert sql_res["thinking_time"] == 0
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=8").fetchone()
        assert sql_res["event_type"] == EventTypes.REPETITION
        assert sql_res["acq_reps"] == 2
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] <= 10 # Depends on CPU load.
        assert sql_res["new_interval"] == 0
        assert sql_res["thinking_time"] == 0
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=9").fetchone()
        assert sql_res["event_type"] == EventTypes.REPETITION
        assert sql_res["acq_reps"] == 3
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] <= 10 # Depends on CPU load.
        assert sql_res["new_interval"] > 0
        assert sql_res["thinking_time"] == 0
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=10").fetchone()
        assert sql_res["event_type"] == EventTypes.SAVED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 1

        sql_res = self.database().con.execute(\
            "select * from log where _id=11").fetchone()
        assert sql_res["event_type"] == EventTypes.STOPPED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=12").fetchone()
        assert sql_res["event_type"] == EventTypes.STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from log where _id=13").fetchone()
        assert sql_res["event_type"] == EventTypes.STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from log where _id=14").fetchone()
        assert sql_res["event_type"] == EventTypes.LOADED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 1

        sql_res = self.database().con.execute(\
            "select * from log where _id=15").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_FACT        
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=16").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_CARD
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=17").fetchone()
        assert sql_res["event_type"] == EventTypes.DELETED_CARD       
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=18").fetchone()
        assert sql_res["event_type"] == EventTypes.DELETED_FACT
        assert sql_res["object_id"] is not None

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
        MnemosyneTest.teardown(self)
            
        file(os.path.join(os.getcwd(), "dot_test", "history", "userid_001.bz2"), "w")
        os.remove(os.path.join(os.getcwd(), "dot_test", "config"))

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)

        assert self.config()["user_id"] == "userid"
        
    def test_recover_user_id_2(self):
        assert self.config()["user_id"] is not None
        MnemosyneTest.teardown(self)
            
        file(os.path.join(os.getcwd(), "dot_test", "history", "userid_machine_001.bz2"), "w")
        os.remove(os.path.join(os.getcwd(), "dot_test", "config"))

        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)

        assert self.config()["user_id"] == "userid"
        
    def test_log_index_of_last_upload_1(self):
        assert self.log().log_index_of_last_upload() == 0
        
    def test_log_index_of_last_upload_2(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2", "user_%s_2.bz2" % machine_id]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2

    def test_log_index_of_last_upload_3(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2"]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 1
        
    def test_log_index_of_last_upload_4(self):
        machine_id = self.config().machine_id()
        for filename in ["user_005.bz2"]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 5
        
    def test_log_index_of_last_upload_5(self):
        machine_id = self.config().machine_id()
        for filename in ["user_othermachine_005.bz2"]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 0
        
    def test_log_index_of_last_upload_6(self):
        machine_id = self.config().machine_id()
        for filename in ["user_othermachine_005.bz2", "user_%s_2.bz2" % machine_id]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2
        
    def test_log_index_of_last_upload_7(self):
        machine_id = self.config().machine_id()
        for filename in ["user_001.bz2", "user_othermachine_005.bz2", "user_%s_2.bz2" % machine_id]:
            file(os.path.join(os.getcwd(), "dot_test", "history", filename), "w")
        assert self.log().log_index_of_last_upload() == 2
        
    def test_log_upload(self):
        machine_id_file = os.path.join(self.mnemosyne.config().config_dir, "machine.id")
        f = file(machine_id_file, "w")
        print >> f, "TESTMACHINE"
        f.close()
        self.config().change_user_id("UPLOADTEST")
        self.config()["max_log_size_before_upload"] = 1   
        MnemosyneTest.teardown(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()       
        MnemosyneTest.teardown(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()         
        MnemosyneTest.teardown(self)
        
        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()  

    def test_log_upload_bad_server(self):
        # Most reliable way of setting this variable is throug config.py, otherwise
        # it will stay alive in a dangling imported userconfig.
        config_py_file = os.path.join(self.mnemosyne.config().config_dir, "config.py")
        f = file(config_py_file, "w")
        print >> f, "science_server = \"noserver:80\""
        f.close()
        
        machine_id_file = os.path.join(self.mnemosyne.config().config_dir, "machine.id")
        f = file(machine_id_file, "w")
        print >> f, "TESTMACHINE"
        f.close()
        self.config().change_user_id("UPLOADTEST")
        self.config()["max_log_size_before_upload"] = 1
        MnemosyneTest.teardown(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))   
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()       
        MnemosyneTest.teardown(self)

        self.mnemosyne = Mnemosyne(upload_science_logs=True, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()         
