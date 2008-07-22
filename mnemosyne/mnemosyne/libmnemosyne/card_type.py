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
    
    def __init__(self, id, name, description,
                 visible=True, can_be_unregistered=True):
        
        print 'init card type', name

        self.type                = "card_type"
        self.id                  = id
        self.name                = name
        self.description         = description
        self.visible             = visible
        self.can_be_unregistered = self.can_be_unregistered
        self.a_on_top_of_q       = False




    ##########################################################################
    #
    # Widget and widget class properties.
    #
    #  TODO: make into regular attributes once debug code is no more needed.
    #
    ########################################################################## 
        
    def set_widget_class(self, widget_class):
        print 'set widget class', widget_class
        self.widget_class = widget_class
        
    def _set_widget_class(self, widget_class):
        print 'set widget class', widget_class
        self._widget_class = widget_class

    def _get_widget_class(self):
        return self._widget_class

    widget_class = property(_get_widget_class, _set_widget_class)


     
    def _set_widget(self, widget):
        print 'set widget', widget
        self._widget = widget

    def _get_widget(self):
        return self._widget

    widget = property(_get_widget, _set_widget)

    

    ##########################################################################
    #
    # Functions to be implemented by the specific card types.
    #
    ########################################################################## 

    def new_cards(self):
        raise NotImplementedError

    def update_cards(self):
        raise NotImplementedError
