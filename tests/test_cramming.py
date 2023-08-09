#
# test_cramming.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class Widget(MainWidget):

    def show_question(self, question, option0, option1, option2):
        if option1 == "&Delete":
            return 1
        raise NotImplementedError


class TestCrammingScheduler(MnemosyneTest):

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
        self.mnemosyne.components.append(\
            ("test_cramming", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.gui_for_component["CramAll"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.config()["study_mode"] = "CramAll"
        self.mnemosyne.start_review()

    def test_1(self):
        from mnemosyne.libmnemosyne.schedulers.cramming import Cramming

        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "3", "b": "b"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        fact_data = {"f": "4", "b": "b"}
        card_4 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        card_4.next_rep -= 1000
        self.database().update_card(card_4)
        self.review_controller().reset()

        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 4
        assert self.database().scheduler_data_count(Cramming.WRONG) == 0
        self.review_controller().grade_answer(0)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 3
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        self.review_controller().grade_answer(5)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 2
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        # Fail the cards a couple of times.
        for i in range(8):
            self.review_controller().grade_answer(0)
        # Pass the cards a couple of times.
        for i in range(8):
            self.review_controller().grade_answer(5)

    def test_reset(self):
        from mnemosyne.libmnemosyne.schedulers.cramming import Cramming

        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "3", "b": "b"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        fact_data = {"f": "4", "b": "b"}
        card_4 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=["default"])[0]
        card_4.next_rep -= 1000
        self.database().update_card(card_4)
        self.review_controller().reset()

        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 4
        assert self.database().scheduler_data_count(Cramming.WRONG) == 0
        assert self.review_controller().counters() == (0, 4, 4)
        self.review_controller().grade_answer(0)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 3
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        assert self.review_controller().counters() == (1, 3, 4)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        assert self.database().scheduler_data_count(Cramming.UNSEEN) == 3
        assert self.database().scheduler_data_count(Cramming.WRONG) == 1
        assert self.review_controller().counters() == (1, 3, 4)

    def test_2(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().show_new_question()
        self.controller().delete_current_card()
        assert self.review_controller().card == None

    def test_3(self): # suffers from some sort of race condition with the finalise.
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().counters()

        self.mnemosyne.finalise()

        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_cramming", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.mnemosyne.start_review()

        assert self.scheduler().name == "cramming"

    def test_4(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().reset()
        self.review_controller().show_new_question()
        self.database().unload()
        self.review_controller().reset()
        self.restart()
