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
