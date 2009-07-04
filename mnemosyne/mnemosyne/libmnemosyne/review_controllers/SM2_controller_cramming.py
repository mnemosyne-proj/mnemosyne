#
# SM2_controller_cramming.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.review_controllers.SM2_controller \
     import SM2Controller
from mnemosyne.libmnemosyne.schedulers.cramming import Cramming


class SM2ControllerCramming(SM2Controller):

    def grade_answer(self, grade):
        card_to_grade = self.card
        old_grade = card_to_grade.grade
        self.update_counters(old_grade, grade)
        if self.scheduler().allow_prefetch():
            self.new_question()
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            self.database().save()
        else:
            interval = self.scheduler().grade_answer(card_to_grade, grade)
            self.database().update_card(card_to_grade, repetition_only=True)
            self.database().save()
            self.new_question()
        self.widget.update_status_bar()
        if self.config()["show_intervals"] == "statusbar":
            self.review_widget().update_status_bar(_("Returns in") + " " + \
                  str(interval) + _(" day(s)."))

    def get_counters(self):
        db = self.database()
        return db.scheduler_data_count(Cramming.WRONG), \
            db.scheduler_data_count(Cramming.UNSEEN), db.active_count()

    def reload_counters(self):
        pass

    def update_counters(self, old_grade, new_grade):
        pass
    
    def update_grades_area(self):
        self.widget.enable_grades(self.grades_enabled)
        if self.grades_enabled:
            self.widget.set_default_grade(5)
