##############################################################################
#
# ui_controller_main.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# UiControllerMain
#
##############################################################################

class UiControllerMain(Plugin):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, widget,
                 name, description, can_be_unregistered=True):

        self.type                = "ui_controller_main"
        self.widget              = widget
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered


    ##########################################################################
    #
    # Functions to be implemented by the actual controller.
    #
    ##########################################################################
    


    # TODO: list calls made back to widget
