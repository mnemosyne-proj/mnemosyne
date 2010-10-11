#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.UDP_server.UDP_widget import UDP_Widget
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget, UDP_Widget):
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
                
    def show_answer(self):
        self.callback()        
           
    def grade_answer(self, grade):
        self.callback(grade)

    def set_question_box_visible(self, is_visible):
        self.callback(is_visible)
                    
    def set_answer_box_visible(self, is_visible):
        self.callback(is_visible)
        
    def set_question_label(self, text):
        self.callback(text)
        
    def set_question(self, text):
        self.callback(text)

    def set_answer(self, text):
        self.callback(text)
        
    def clear_question(self):
        self.callback()
            
    def clear_answer(self):
        self.callback()

    def update_show_button(self, text, is_default, is_enabled):
        self.callback(text, is_default, is_enabled)

    def set_grades_enabled(self, is_enabled):
        self.callback(is_enabled)
        
    def set_default_grade(self, grade):
        self.callback(grade)

    def update_status_bar(self):
        self.callback()




       
