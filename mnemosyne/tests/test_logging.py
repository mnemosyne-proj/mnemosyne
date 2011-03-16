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
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()
        
    def test_logging(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().new_question()
        self.review_controller().grade_answer(1)
        self.review_controller().grade_answer(4)

        self.mnemosyne.finalise()
        self.restart()
        card_type = self.card_type_by_id("1")
        fact_data = {"f": "2", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()        
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
        assert sql_res["event_type"] == EventTypes.ADDED_FACT
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from log where _id=5").fetchone()
        assert sql_res["event_type"] == EventTypes.ADDED_TAG
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
        card_type_2 = self.card_type_by_id("2")
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
        card_type_2 = self.card_type_by_id("1")
        card_1  = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])        
        assert self.database().con.execute(\
            """select _id from log order by _id limit 1""").fetchone()[0] \
            == log_index      
        
