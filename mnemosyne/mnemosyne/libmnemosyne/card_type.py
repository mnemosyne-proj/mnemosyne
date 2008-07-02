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

card_types = {}

class CardType:

    def __init__(self, name, widget_class, new_cards_function=None,
                 update_cards_function=None):

        self.name         = name
        self.widget_class = widget_class
        self.new_card     = new_cards_function
        self.update_card  = update_cards_function



##############################################################################
#
# get_card_types
#
##############################################################################

def get_card_types():
    return card_types



##############################################################################
#
# get_card_type_by_name
#
##############################################################################

def get_card_type_by_name(name):
    return card_types[name]



##############################################################################
#
# register_card_type
#
##############################################################################

def register_card_type(name, widget_class, new_cards_function=None,
                 update_cards_function=None):

    global card_types
    
    card_types[name] = CardType(name, widget_class, new_cards_function,
                                update_cards_function)
