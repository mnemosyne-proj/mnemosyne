#
# review_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class ReviewWidget(UiComponent):
    
    """Describes the interface that the review widget needs to implement
    in order to be used by the review controller.

    Note that also the review widget is instantiated late, even though we
    always need one right from the start of the program. The reason is that
    there could be many review widgets defined through plugins, and
    instantiating them all at the start of the program could be slow,
    especially on mobile devices.

    """

    component_type = "review_widget"
        
    def set_question_box_visible(self, is_visible):
        pass
        
    def set_answer_box_visible(self, is_visible):
        pass
        
    def set_question_label(self, text):
        pass
        
    def set_question(self, text):
        pass
        
    def set_answer(self, text):
        pass
        
    def clear_question(self): 
        pass
        
    def clear_answer(self): 
        pass
        
    def update_show_button(self, text, is_default, is_enabled): 
        pass

    def set_grades_enabled(self, is_enabled):

        """Enable whole grade area, including title."""
        
        pass
    
    def set_grade_enabled(self, grade, is_enabled):

        """Enable just a single grade button."""
        
        pass
    
    def set_default_grade(self, grade):
        pass
        
    def set_grades_title(self, text): 
        pass
            
    def set_grade_text(self, grade, text): 
        pass
            
    def set_grade_tooltip(self, grade, text): 
        pass

    def update_status_bar(self, message=None):
        pass 
