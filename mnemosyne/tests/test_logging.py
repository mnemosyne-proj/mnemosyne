#
# test_logging.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MyMainWidget(MainWidget):

    def question_box(self, a, b, c, d):
        return 0 # Say yes when deleting a card.
            

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

    def test_logging(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "1", "a": "a"}
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        self.ui_controller_review().new_question()
        self.ui_controller_review().grade_answer(0)
        self.ui_controller_review().new_question()
        self.ui_controller_review().grade_answer(1)
        self.ui_controller_review().grade_answer(4)

        self.mnemosyne.finalise()
        self.restart()
        fact_data = {"q": "2", "a": "a"}
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                     grade=0, cat_names=["default"], warn=False)[0]
        self.ui_controller_review().new_question()        
        self.ui_controller_main().delete_current_fact()

        self.log().dump_to_txt_log()

        sql_res = self.database().con.execute(\
            "select * from history where _id=1").fetchone()
        assert sql_res["event"] == self.log().STARTED_PROGRAM

        sql_res = self.database().con.execute(\
            "select * from history where _id=2").fetchone()
        assert sql_res["event"] == self.log().STARTED_SCHEDULER      

        
