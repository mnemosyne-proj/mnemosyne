#
# UDP_review_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class UDP_ReviewWidget(ReviewWidget):
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        self.question_label = ""
        self.question = ""
        self.question_box_visible = True
        self.answer = ""
        self.answer_label = ""
        self.answer_box_visible = True
        self.show_button = ""
        self.show_button_enabled = True              
        self.grade_buttons_enabled = False
        self.status_bar = ""
        
    def set_question_label(self, text):
        self.main_widget().buffer += \
            ("< review_widget.set_question_label(\"%s\")\n" % text)
        
    def set_question(self, text):
        self.question = text

    def clear_question(self):
		self.question = ""
        
    def set_question_box_visible(self, visible):
        self.question_box_visible = visible

    def set_answer(self, text):
        self.answer = text

    def clear_answer(self):
		self.answer = ""
            
    def set_answer_box_visible(self, visible):
        self.answer_box_visible = visible

    def update_show_button(self, text, default, enabled):
        self.show_button = text
        self.show_button_enabled = enabled

    def set_grades_enabled(self, enabled):
        self.grade_buttons_enabled = enabled
        
    def set_default_grade(self, grade):
        pass
        
    def show_answer(self):
        self.review_controller().show_answer()
           
    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def update_status_bar(self):
        scheduled_count, non_memorised_count, active_count = \
                   self.review_controller().counters()
        self.status_bar  = "Sch.: %d Not mem.: %d Act.: %d" % \
            (scheduled_count, non_memorised_count, active_count)



       
