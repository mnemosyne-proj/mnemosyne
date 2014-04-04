#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget):
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        self.callbacks = {}
        
    def set_callback(self, name, callback):
        self.callbacks[name] = callback    

    def redraw_now(self):
        self.callbacks["redraw_now"]()

    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        self.callbacks["set_question_box_visible"](is_visible)

    def set_answer_box_visible(self, is_visible):
        self.callbacks["set_answer_box_visible"](is_visible)
        
    def set_question_label(self, text):
        self.callbacks["set_question_label"](text)

    def set_question(self, text):
        self.callbacks["set_question"](text)
        
    def set_answer(self, text):
        self.callbacks["set_answer"](text)
        
    def clear_question(self):
        self.callbacks["clear_question"]()
        
    def clear_answer(self):
        self.callbacks["clear_answer"]()

    def update_show_button(self, text, is_default, is_enabled):
        self.callbacks["update_show_button"](text, is_default, is_enabled)

    def set_grades_enabled(self, is_enabled):
        self.callbacks["set_grades_enabled"](is_enabled)

    def set_default_grade(self, grade):
        self.callbacks["set_default_grade"](grade)

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        self.callbacks["update_status_bar_counters"]\
            (scheduled_count, non_memorised_count, active_count)
