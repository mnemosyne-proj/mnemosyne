#
# filter.py <Peter.Bienstman@UGent.be>
#


class Filter(object):

    """Code which operates on a string and filters it to achieve extra 
    functionality.  The 'card' argument provides extra context if needed.

    The filters are executed in the order they are listed in the component
    manager. If you really need to make sure that your filter runs before the
    rest, use 'component_manager.register_first', instead of the usual
    'component_manager.register'.

    
    """

    component_type = "filter"

    def run(self, text, card):
        raise NotImplementedError





