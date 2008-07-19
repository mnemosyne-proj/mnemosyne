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

class CardType(object):

    def __init__(self, id, name):
        global card_types
        card_types[id] = self

        print 'init card type', name

        self.name = name
        self.id = id
        
    def set_widget_class(self, widget_class):
        print 'set widget class', widget_class
        self.widget_class = widget_class
        
    def set_widget(self, widget):
        print 'set widget', widget
        self.widget = widget        

    def new_cards(self):
        raise NotImplementedError()

    def update_cards(self):
        raise NotImplementedError()
    


##############################################################################
#
# get_card_types
#
##############################################################################

def get_card_types():
    
    return card_types



##############################################################################
#
# get_card_type_by_id
#
##############################################################################

def get_card_type_by_id(id):
    
    return card_types[id]



##############################################################################
#
# register_card_type
#
##############################################################################

register_card_type(card_type_class, card_widget_class):
    
    c = card_type_class()
    c.set_widget_class(card_widget_class)



##############################################################################
#
# unregister_card_type
#
##############################################################################

# TODO: test

unregister_card_type(card_type_class):

    global card_types

    for id, c in card_types.iteritems():
        if isinstance(c. card_type_class):
            del card_types[id]
            break
