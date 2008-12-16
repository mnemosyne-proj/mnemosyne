#
# review_widget.py <Peter.Bienstman@UGent.be>
#


class ReviewWidget(object):
    
    """Describes the interface that the review widget needs to implement
    in order to be used by the review controller."""
    
    def set_window_title(self, title):
        raise NotImplementedError
        
    def enable_edit_current_card(self, bool):
        raise NotImplementedError
        
    def enable_delete_current_card(self, bool):
        raise NotImplementedError
        
    def enable_edit_deck(self, bool): 
        raise NotImplementedError
        
    def question_box_visible(self, bool):
        raise NotImplementedError
        
    def answer_box_visible(self, bool):
        raise NotImplementedError
        
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
        
    def set_grades_title(self, text): 
        raise NotImplementedError
            
    def set_grade_text(self, grade, text): 
        raise NotImplementedError
            
    def set_grade_tooltip(self, grade, text): 
        raise NotImplementedError
