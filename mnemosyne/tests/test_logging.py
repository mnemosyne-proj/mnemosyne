#
# test_logging.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MyMainWidget(MainWidget):

    def question_box(self, question, b, c, d):
        if question == "Delete this card?":
            return 0 # Yes
        else:
            raise NotImplementedError
            

class TestLogging(MnemosyneTest):
    
    def restart(self):
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_logging", "MyMainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))
        self.review_controller().reset()

    def test_logging(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().new_question()
        self.review_controller().grade_answer(1)
        self.review_controller().grade_answer(4)

        self.mnemosyne.finalise()
        self.restart()
        fact_data = {"q": "2", "a": "a"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().new_question()        
        self.controller().delete_current_fact()

        self.log().dump_to_txt_log()

        sql_res = self.database().con.execute(\
            "select * from history where _id=1").fetchone()
        assert sql_res["event"] == self.log().STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from history where _id=2").fetchone()
        assert sql_res["event"] == self.log().STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from history where _id=3").fetchone()
        assert sql_res["event"] == self.log().LOADED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 0
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=4").fetchone()
        assert sql_res["event"] == self.log().ADDED_FACT
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=5").fetchone()
        assert sql_res["event"] == self.log().ADDED_TAG
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=6").fetchone()
        assert sql_res["event"] == self.log().ADDED_CARD
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=7").fetchone()
        assert sql_res["event"] == self.log().REPETITION
        assert sql_res["acq_reps"] == 1
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] == 0
        assert sql_res["new_interval"] == 0
        assert sql_res["thinking_time"] == 0
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=8").fetchone()
        assert sql_res["event"] == self.log().REPETITION
        assert sql_res["acq_reps"] == 2
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] == 0
        assert sql_res["new_interval"] == 0
        assert sql_res["thinking_time"] == 0
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=9").fetchone()
        assert sql_res["event"] == self.log().REPETITION
        assert sql_res["acq_reps"] == 3
        assert sql_res["ret_reps"] == 0
        assert sql_res["scheduled_interval"] == 0
        assert sql_res["actual_interval"] <= 10 # Depends on CUP load.
        assert sql_res["new_interval"] > 0
        assert sql_res["thinking_time"] == 0  

        sql_res = self.database().con.execute(\
            "select * from history where _id=10").fetchone()
        assert sql_res["event"] == self.log().SAVED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 1

        sql_res = self.database().con.execute(\
            "select * from history where _id=11").fetchone()
        assert sql_res["event"] == self.log().STOPPED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from history where _id=12").fetchone()
        assert sql_res["event"] == self.log().STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from history where _id=13").fetchone()
        assert sql_res["event"] == self.log().STARTED_SCHEDULER

        sql_res = self.database().con.execute(\
            "select * from history where _id=14").fetchone()
        assert sql_res["event"] == self.log().LOADED_DATABASE
        assert sql_res["acq_reps"] == 0
        assert sql_res["ret_reps"] == 0
        assert sql_res["lapses"] == 1

        sql_res = self.database().con.execute(\
            "select * from history where _id=15").fetchone()
        assert sql_res["event"] == self.log().ADDED_FACT        
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=16").fetchone()
        assert sql_res["event"] == self.log().ADDED_CARD
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=17").fetchone()
        assert sql_res["event"] == self.log().DELETED_CARD       
        assert sql_res["object_id"] is not None
        
        sql_res = self.database().con.execute(\
            "select * from history where _id=18").fetchone()
        assert sql_res["event"] == self.log().DELETED_FACT
        assert sql_res["object_id"] is not None
