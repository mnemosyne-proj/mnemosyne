#
# ui_controller_review.py <Peter.Bienstman@UGent.be>
#


class UiControllerReview(object):
    
    """Controls the behaviour of a widget which implements the ReviewWidget
    interface.
    
    """

    def __init__(self):
        self.widget = None
        self.card = None
        self.learning_ahead = False

    def reset(self):
        raise NotImplementedError

    def rollover(self):

        """To be called when a new day starts."""
        
        pass

    def new_question(self, learn_ahead=False):
        raise NotImplementedError    
        
    def show_answer(self):
        raise NotImplementedError
        
    def update_dialog(self):
        raise NotImplementedError
  

