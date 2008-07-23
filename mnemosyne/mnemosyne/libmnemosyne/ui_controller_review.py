##############################################################################
#
# ui_controller.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# UiController
#
##############################################################################

class UiController(Plugin):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, widget,
                 name, description, can_be_unregistered=True):

        self.type                = "ui_controller"
        self.widget              = widget
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered




    ##########################################################################
    #
    # Functions to be implemented by the actual controller.
    #
    ##########################################################################
    
    def new_question(self):
        raise NotImplementedError



    # TODO: list calls made back to widget
