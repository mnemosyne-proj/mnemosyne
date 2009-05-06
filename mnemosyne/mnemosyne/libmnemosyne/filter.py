#
# filter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Filter(Component):

    """Code which operates on a string and filters it to achieve extra 
    functionality.  The 'card' argument provides extra context if needed.

    The filters are executed in the order they are listed in the component
    manager. If you really need to make sure that your filter runs before the
    rest, set 'in_front=True' as argument in 'component_manager.register'.
    
    """

    component_type = "filter"

    def run(self, text, card):
        raise NotImplementedError





