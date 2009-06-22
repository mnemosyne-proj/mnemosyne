#
# main_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class MainWidget(UiComponent):
    
    """Describes the interface that the main widget needs to implement
    in order to be used by the main controller.

    """

    component_type = "main_widget"
    
    def information_box(self, message):
        pass
            
    def question_box(self, question, option0, option1, option2):
        pass
    
    def error_box(self, message):
        pass

    def enable_edit_current_card(self, enabled):
        pass
        
    def enable_delete_current_card(self, enabled):
        pass
        
    def enable_browse_cards(self, enable): 
        pass
    
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

    def run_browse_cards_dialog(self):
        pass
    
    def run_configuration_dialog(self):
        pass

    def run_show_statistics_dialog(self):
        pass
