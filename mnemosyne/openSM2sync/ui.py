#
# ui.py <Peter.Bienstman@UGent.be>
#

class UI(object):

    """Interface that needs to be implemented by the Ui object used in the
    Client and the Server.

    """

    def information_box(self, message):
        raise NotImplementedError
    
    def error_box(self, message):
        raise NotImplementedError
    
    def question_box(self, question, option0, option1, option2):

        """Returns 0, 1 or 2."""
                
        raise NotImplementedError

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



