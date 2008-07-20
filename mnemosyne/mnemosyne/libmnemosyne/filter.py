##############################################################################
#
# filter.py <Peter.Bienstman@UGent.be>
#
##############################################################################



##############################################################################
#
# Filter
#
#  Code which operates on the Q and A strings and filters it to achieve
#  extra functionality.
#
##############################################################################

_filters = []

# TODO: flesh out.

class Filter(object):

    def __init__():
        pass

    def run(self, text):
        pass



##############################################################################
#
# register_filter
#
##############################################################################

register_card_type(card_type_class, card_widget_class):
    
    c = card_type_class()
    c.set_widget_class(card_widget_class)



##############################################################################
#
# unregister_filter
#
##############################################################################

# TODO: test

unregister_card_type(card_type_class):

    global card_types

    for id, c in card_types.iteritems():
        if isinstance(c. card_type_class):
            del card_types[id]
            break



    
