#
# SM2_controller_cramming.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.review_controllers.SM2_controller \
     import SM2Controller
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming


class SM2ControllerCramming(SM2Controller):

    def grade_answer(self, grade):
        self.flush_sync_server()
        card_to_grade = self.card
        old_grade = card_to_grade.grade
        self.update_counters(old_grade, grade)
        self.rep_count += 1
        if self.scheduler().is_prefetch_allowed(card_to_grade):
            self.show_new_question()
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            if self.rep_count % self.config()["save_after_n_reps"] == 0:
                self.database().save()
        else:
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            if self.rep_count % self.config()["save_after_n_reps"] == 0:
                self.database().save()
            self.show_new_question()
        self.review_widget().update_status_bar_counters()
        if self.config()["show_intervals"] == "status_bar":
            self.main_widget().update_status_bar_message(_("Returns in") + \
                " " + str(interval) + _(" day(s)."))

    def counters(self):
        db = self.database()
        max_ret_reps = 1 if self.new_only else -1
        return db.scheduler_data_count(Cramming.WRONG, max_ret_reps), \
            db.scheduler_data_count(Cramming.UNSEEN, max_ret_reps),  \
            db.active_count()

    def reload_counters(self):
        pass

    def update_counters(self, old_grade, new_grade):
        pass

    def update_grades_area(self):
        self.review_widget().set_grades_enabled(self.grades_enabled)
        if self.grades_enabled:
            self.review_widget().set_default_grade(5)
