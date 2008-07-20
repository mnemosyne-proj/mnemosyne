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

_card_types = {}

class CardType(object):

    @staticmethod
    def by_id(id):
        return _card_types[id]

    @staticmethod
    def all():
        return _card_types

    def __init__(self, id, name):
        global card_types
        card_types[id] = self

        print 'init card type', name

        self.name = name
        self.id = id


        
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



    def new_cards(self):
        raise NotImplementedError()

    def update_cards(self):
        raise NotImplementedError()
    


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
