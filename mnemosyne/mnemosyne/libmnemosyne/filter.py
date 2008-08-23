#
# filter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Filter(Component):

    """Code which operates on the fact data and filters it to achieve extra 
    functionality.
    
    """

    def run(self, text, fact):
        raise NotImplementedError





