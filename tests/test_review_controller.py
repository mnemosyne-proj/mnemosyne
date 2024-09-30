#
# test_review_controller.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

expected_scheduled_count = None

class MyReviewWidget(ReviewWidget):

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        if expected_scheduled_count is not None:
            assert scheduled_count == expected_scheduled_count

    def redraw_now(self):
        pass


class TestReviewController(MnemosyneTest):

    def setup_method(self):
        global expected_scheduled_count
        expected_scheduled_count = None
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
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("test_review_controller", "MyReviewWidget")]
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditCardDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"), automatic_upgrades=False)
        self.review_controller().reset()

    def test_1(self):
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"f": "question" + str(i),
                         "b": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_with_id("1")
            else:
                card_type = self.card_type_with_id("2")
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60
                self.database().update_card(card)
        self.review_controller().set_render_chain("default")
        self.review_controller().show_new_question()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().show_answer()
        assert self.review_controller().card == card_1
        assert self.review_controller().counters() == (1, 0, 15)
        self.review_controller().grade_answer(0)
        assert self.review_controller().counters() == (0, 1, 15)
        self.review_controller().grade_answer(2)
        assert self.review_controller().counters() == (0, 0, 15)
        self.review_controller().next_rep_string(0)
        self.review_controller().next_rep_string(1)
        self.review_controller().next_rep_string(2)

    def test_2(self):
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"f": "question" + str(i),
                         "b": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_with_id("1")
            else:
                card_type = self.card_type_with_id("2")
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            if i == 0:
                card_1 = card
                card.next_rep -= 1000 * 24 * 60 * 60
                self.database().update_card(card)
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.review_controller().reload_counters()
        assert self.review_controller().counters() == (1, 0, 15)
        self.review_controller().grade_answer(0)
        self.review_controller().reload_counters()
        assert self.review_controller().counters() == (0, 1, 15)
        self.review_controller().grade_answer(2)
        self.review_controller().reload_counters()
        assert self.review_controller().counters() == (0, 0, 15)

        self.mnemosyne.review_widget().set_grade_enabled(1, True)

    def test_reset_but_try_to_keep_current_card_turned_inactive(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["forbidden"])[0]
        self.review_controller().show_new_question()
        assert self.review_controller().card == card

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("active")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        assert self.review_controller().card == card
        self.review_controller().reset_but_try_to_keep_current_card()
        assert self.review_controller().card is None

    def test_last_card(self):
        card_type = self.card_type_with_id("1")
        for data in ["1", "2", "3"]:
            fact_data = {"f": data, "b": data}
            self.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[])
        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        for i in range(5):
            self.review_controller().grade_answer(0)
            self.review_controller().show_answer()
        for i in range(2):
            self.review_controller().grade_answer(2)
            self.review_controller().show_answer()
        for i in range(6):
            self.review_controller().grade_answer(0)
            self.review_controller().show_answer()

    def test_counters(self):
        global expected_scheduled_count
        card_type = self.card_type_with_id("1")
        fact_data = {"f": '1', "b": '1'}
        card = self.controller().create_new_cards(fact_data, card_type, grade=5, tag_names=[])[0]
        card.next_rep = 0
        self.database().update_card(card)
        expected_scheduled_count = 1
        self.review_controller().show_new_question()
        assert self.review_controller().scheduled_count == 1
        assert self.review_controller().counters()[0] == 1
        self.review_controller().show_answer()
        expected_scheduled_count = 0
        self.review_controller().grade_answer(0)
        assert self.review_controller().scheduled_count == 0
        assert self.review_controller().counters()[0] == 0

    def test_counters_prefetch(self):
        global expected_scheduled_count
        card_type = self.card_type_with_id("1")
        for data in ['1', '2', '3', '4']:
            fact_data = {"f": data, "b": data}
            card = self.controller().create_new_cards(fact_data, card_type, grade=5, tag_names=[])[0]
            card.next_rep = 0
            self.database().update_card(card)
        expected_scheduled_count = 4
        self.review_controller().show_new_question()
        assert self.review_controller().scheduled_count == 4
        assert self.review_controller().counters()[0] == 4
        self.review_controller().show_answer()
        expected_scheduled_count = 3
        self.review_controller().grade_answer(3)
        assert self.review_controller().scheduled_count == 3
        assert self.review_controller().counters()[0] == 3
