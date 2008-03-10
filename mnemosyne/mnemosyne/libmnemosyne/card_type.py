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

card_types = []

class CardType:

    def __init__(self, name, widget_class, new_cards_function=None,
                 update_cards_function=None):

        self.name = name
        self.widget_class = widget_class
        self.new_cards_function = new_cards_function
        self.update_cards_function = update_cards_function



##############################################################################
#
# register_card_type
#
##############################################################################

def register_card_type(name, widget_class, new_cards_function=None,
                 update_cards_function=None):

    global card_types
    
    card_types.append(CardType(name, widget_class, new_cards_function,
                               update_cards_function))
