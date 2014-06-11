#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget):  

    def redraw_now(self):
        pass

    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        pass

    def set_answer_box_visible(self, is_visible):
        # TODO
        pass
        
    def set_question_label(self, text):
        self.component_manager().activity.setQuestionLabel(self.text)

    def set_question(self, text):
        self.question = text
        
    def set_answer(self, text):
        self.answer = text
        
    def reveal_question(self):
        self.component_manager().activity.setQuestion(self.question)
        
    def reveal_answer(self):
        self.component_manager().activity.setAnswer(self.answer)
        
    def clear_question(self):
        self.question = ""
        self.reveal_question()
        
    def clear_answer(self):
        self.answer = ""
        self.reveal_answer()

    def update_show_button(self, text, is_default, is_enabled):
        pass

    def set_grades_enabled(self, is_enabled):
        pass

    def set_default_grade(self, grade):
        pass

    def update_status_bar_counters(self):
        # TODO
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()

