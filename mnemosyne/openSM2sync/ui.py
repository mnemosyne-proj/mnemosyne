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
        raise NotImplementedError

    def set_progress_text(self, text):
        pass
    
    def set_progress_range(self, minimum, maximum):
        pass

    def set_progress_value(self, value):
        pass
