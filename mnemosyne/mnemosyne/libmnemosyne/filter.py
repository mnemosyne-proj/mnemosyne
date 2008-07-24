##############################################################################
#
# filter.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from libmnemosyne.plugin import Plugin



##############################################################################
#
# Filter
#
#  Code which operates on the Q and A strings and filters it to achieve
#  extra functionality.
#
#  Filters which have side effects (e.g. opening an external program) should
#  set run_once to True, as the filters  be run several times
#
##############################################################################

class Filter(Plugin):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, name, description, can_be_unregistered=True):

        self.type                = "filter"
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered



    ##########################################################################
    #
    # Function to be implemented by the actual filter.
    #
    ##########################################################################
        
    def run(self, text):
        raise NotImplementedError




    
