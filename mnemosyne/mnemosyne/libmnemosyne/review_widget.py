#
# review_widget.py <Peter.Bienstman@UGent.be>
#


class ReviewWidget(object):
    
    """Describes the interface that the review widget needs to implement
    in order to be used by the review controller.

    """

    component_type = "review_widget"
    
    def enable_edit_current_card(self, enabled):
        pass
        
    def enable_delete_current_card(self, enabled):
        pass
        
    def enable_edit_deck(self, enable): 
        pass
        
    def question_box_visible(self, visible):
        pass
        
    def answer_box_visible(self, visible):
        pass
        
    def set_question_label(self, text):
        raise NotImplementedError
        
    def set_question(self, text):
        raise NotImplementedError
        
    def set_answer(self, text):
        raise NotImplementedError
        
    def clear_question(self): 
        raise NotImplementedError
        
    def clear_answer(self): 
        raise NotImplementedError
        
    def update_show_button(self, text, default, enabled): 
        raise NotImplementedError

    def set_enable_grades(self, enabled): 
        raise NotImplementedError
    
    def grade_4_default(self, use_4):
        pass
        
    def set_grades_title(self, text): 
        pass
            
    def set_grade_text(self, grade, text): 
        pass
            
    def set_grade_tooltip(self, grade, text): 
        pass

    def update_status_bar(self, message=None):
        pass 
