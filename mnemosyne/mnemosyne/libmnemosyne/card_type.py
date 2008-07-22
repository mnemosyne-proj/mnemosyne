##############################################################################
#
# Card type <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# CardType
#
##############################################################################

class CardType(Plugin):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, id, name, description="",
                 visible=True, can_be_unregistered=True):

        self.type                = "card_type"
        self.id                  = id
        self.name                = name
        self.description         = description
        self.widget_class        = None
        self.widget              = None
        self.css                 = ""
        self.visible             = visible
        self.can_be_unregistered = can_be_unregistered
        self.a_on_top_of_q       = False



    ##########################################################################
    #
    # Functions to be implemented by the specific card types.
    #
    ########################################################################## 

    def new_cards(self):
        raise NotImplementedError

    def update_cards(self):
        raise NotImplementedError
