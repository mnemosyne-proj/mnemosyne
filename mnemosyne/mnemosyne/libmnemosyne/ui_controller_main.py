#
# ui_controller_main.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UiControllerMain(Component):

    """A collection of logic used by the main Mnemosyne window and some related
    widgets.  The logic related to the review process is split out in a
    separated controller class, to allow that to be swapped out easily.

    """

    def __init__(self, name="", description=""):    
        self.name = None
        self.description = None
        self.widget = None
        
    def add_cards(self):
        raise NotImplementedError

    def create_new_cards(self, fact_data, card_type, grade, cat_names):
        raise NotImplementedError


    # TODO: list calls made back to widget.

    # information_box(self, message, OK_string)
    # question_box(self, question, option0, option1, option2):
