#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import _review_wdgt as _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget):

    def set_question_box_visible(self, is_visible):
        _.set_question_box_visible(is_visible)
        
    def set_answer_box_visible(self, is_visible):
        _.set_answer_box_visible(is_visible)
        
    def set_question_label(self, text):
        _.set_question_label(text.encode("utf-8"))
        
    def set_question(self, text):
        _.set_question(text.encode("utf-8"))
        
    def set_answer(self, text):
        _.set_answer(text.encode("utf-8"))
        
    def clear_question(self): 
        _.clear_question()
        
    def clear_answer(self): 
        _.clear_answer ()
        
    def update_show_button(self, text, is_default, is_enabled): 
        _.update_show_button(text.encode("utf-8"), is_default, is_enabled)

    def set_grades_enabled(self, is_enabled):
        _.set_grades_enabled(is_enabled)
    
    def set_grade_enabled(self, grade, is_enabled):
        _.set_grade_enabled(is_enabled)
    
    def set_default_grade(self, grade):
        _.set_default_grade(grade)
        
    def set_grades_title(self, text): 
        _.set_grades_title(text.encode("utf-8"))
            
    def set_grade_text(self, grade, text): 
        _.set_grade_text(grade, text.encode("utf-8"))
            
    def set_grade_tooltip(self, grade, text): 
        _.set_grade_tooltip(grade, text.encode("utf-8"))

    def update_status_bar_counters(self):
        _.update_status_bar_counters()

    def repaint_now(self):
        _.repaint_now()
