#
# ui_controller_review.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UiControllerReview(Component):
    
    """Controls the behaviour of a widget which implements the ReviewWidget
    interface.
    
    """

    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.widget = None
        self.card = None

    def clear(self):
        raise NotImplementedError        

    def new_question(self):
        raise NotImplementedError    
        
    def show_answer(self):
        raise NotImplementedError
        
    def update_dialog(self):
        raise NotImplementedError
  

