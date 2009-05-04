#
# ui_components.py <Peter.Bienstman@UGent.be>
#

class UIComponent(object):

    component_type = "ui_component"
    used_for = None



class MainWidget(UIComponent):
    
    """Describes the interface that the main widget needs to implement
    in order to be used by the main controller.

    """
    
    def after_mnemosyne_init(self):

        """If the widget needs to do some initialisation which requires
        libmnemosyne to be already initialised, this can go here.

        """
        
        pass
    
    def init_review_widget(self):

        """At the very least, this function has to inform the controller
        about its review widget.

        """
        
        pass
    
    def information_box(self, message):
        pass
            
    def question_box(self, question, option0, option1, option2):
        pass
    
    def error_box(self, message):
        pass
        
    def show_exception(self, exception):
        if exception.info:
            exception.msg += "\n" + exception.info
        self.error_box(exception.msg)
    
    def save_file_dialog(self, path, filter, caption=""):
        pass
    
    def open_file_dialog(self, path, filter, caption=""):
        pass

    def set_window_title(self, title):
        pass
    
    def run_add_card_dialog(self):
        pass

    def run_edit_fact_dialog(self, fact, allow_cancel=True):
        pass
    
    def run_card_appearance_dialog(self):
        pass

    def run_manage_card_types_dialog(self):
        pass


class ReviewWidget(UIComponent):
    
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
