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
        pass
        
    def information_box(self, message):
        print message
            
    def question_box(self, question, option0, option1, option2):

        """Returns 0, 1 or 2."""
        
        raise NotImplementedError
    
    def error_box(self, message):
        print message

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
        
        raise NotImplementedError
    
    def open_file_dialog(self, path, filter, caption=""):
        raise NotImplementedError

    def set_window_title(self, title):
        pass
    
    def set_progress_text(self, text):

        """Resets all the attributes of the progress bar if one is still open,
        and displays 'text'.

        """
        
        pass
    
    def set_progress_range(self, minimum, maximum):

        """If minimum and maximum are zero, this is just a busy dialog.
        Should be the default for set_progress_text.

        """
        
        pass
    
    def set_progress_update_interval(self, update_interval):

        """Sometimes updating the progress bar for a single step takes longer
        than doing the actual processing. In this case, it is useful to set
        'update_interval' and the progress bar will only be updated every
        'update_interval' steps.

        """
        
        pass
    
    def set_progress_value(self, value):

        """If value is maximum or beyond, the dialog closes."""
        
        pass

    def close_progress(self):

        """Convenience function for closing a busy dialog."""
        
        pass


        
