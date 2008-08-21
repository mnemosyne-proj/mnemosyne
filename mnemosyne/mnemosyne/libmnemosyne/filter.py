#
# filter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Filter(Component):

    """Code which operates on the Q and A strings and filters it to achieve
    extra functionality.

    There are two types of filters:

    'fact_filter', which operates on the fact data before it has been
    assembled in questions and answers.
    
    'card_filter', which runs on the questions and answers assembled into
    cards.
    
    """

    def run(self, text, obj):
        
        """Function to be implemented by the actual filter.  obj contains
        the fact or the card in case a filter needs that extra information.
        raise NotImplementedError
        
        """
        
        raise NotImplementedError





