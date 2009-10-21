#
# ui.py <Peter.Bienstman@UGent.be>
#

class UI(object):

    """Interface that needs to be implemented by the Ui object passed
    to the constructer of the client.

    """

    def information_box(self, message):
        raise NotImplementedError
            
    def question_box(self, question, option0, option1, option2):
        raise NotImplementedError
    
    def error_box(self, message):
        raise NotImplementedError

    def status_bar_message(self, message):
        pass

    def get_progress_dialog(self):

        """Returns a new progress dialog with the interface specified below."""
        
        pass        



class ProgressDialog(object):

    def set_range(self, minimum, maximum):
        pass

    def set_text(self, text):
        pass

    def set_value(self, value):
        pass
