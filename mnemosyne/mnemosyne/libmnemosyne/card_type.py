##############################################################################
#
# Card type <Peter.Bienstman@UGent.be>
#
##############################################################################

##############################################################################
#
# CardType
#
##############################################################################

class CardType:

    def __init__(self, widget_factory, name):

        self.widget_factory = widget_factory
        self.name = name

    def widget(self):

        return self.widget_factory()

    def new_cards(self, data):

        pass

    def update_cards(self, data):

        pass
        
