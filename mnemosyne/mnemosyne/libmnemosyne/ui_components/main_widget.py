#
# main_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class MainWidget(UiComponent):
    
    """Describes the interface that the main widget needs to implement
    in order to be used by the main controller.

    """

    component_type = "main_widget"

    instantiate = UiComponent.IMMEDIATELY
    
    def activate(self):
        raise NotImplementedError
        
    def information_box(self, message):
        raise NotImplementedError
            
    def question_box(self, question, option0, option1, option2):
        raise NotImplementedError
    
    def error_box(self, message):
        raise NotImplementedError

    def status_bar_message(self, message):
        pass

    def add_to_status_bar(self, widget):
        pass

    def clear_status_bar(self):
        pass

    def enable_edit_current_card(self, enabled):
        pass
        
    def enable_delete_current_card(self, enabled):
        pass
        
    def enable_browse_cards(self, enable): 
        pass
    
    def save_file_dialog(self, path, filter, caption=""):

        """Should ask for confirmation on overwrite."""
        
        pass
    
    def open_file_dialog(self, path, filter, caption=""):
        pass

    def set_window_title(self, title):
        pass

    def get_progress_dialog(self):

        """Convenience function to be able to use main_widget in libraries
        which don't know about libmnemosyne (like openSM2sync.

        """
        
        return self.component_manager.get_current("progress_dialog")\
                   (self.component_manager)
        
