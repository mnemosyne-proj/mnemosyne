#
# ui_controller_main.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UiControllerMain(Component):

    """A collection of logic used by the main Mnemosyne window.  For
    convenience, logic of some related widgets (like the "Add cards" widget)
    is also included, in as far as it does not need to refer back to a widget
    other than the main widget.
    The logic related to the review process is split out in a separated
    controller class, to allow that to be swapped out easily

    """

    def __init__(self, name, description, widget):
        self.name = name
        self.description = description
        self.widget = widget

    def create_new_cards(self, fact_data, card_type, grade, cat_names):
        raise NotImplementedError


    # TODO: list calls made back to widget.