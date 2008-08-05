##############################################################################
#
# filter.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.component import Component



##############################################################################
#
# Filter
#
#  Code which operates on the Q and A strings and filters it to achieve
#  extra functionality.
#
#  There are two types of filters:
#
#    'fact_filter', which operates on the fact data before it has been
#    assembled in questions and answers.
#
#    'card_filter', which runs on the questions and answers assembled into
#    cards.
#
##############################################################################

class Filter(Component):

    ##########################################################################
    #
    # Function to be implemented by the actual filter.
    #
    ##########################################################################
        
    def run(self, text):
        raise NotImplementedError




    
