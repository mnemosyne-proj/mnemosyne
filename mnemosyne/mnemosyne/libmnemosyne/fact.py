##############################################################################
#
# fact.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import datetime, md5

from mnemosyne.libmnemosyne.database import *



##############################################################################
#
# Fact
#
#   Basic unit of information from which several cards can be derived.
#   The fields are stored in a dictionary.
#
# TODO: make list of common keys for standardisation.
# TODO: store facts in a separate database? They might not be needed for
# e.g. mobile clients.
#
##############################################################################

class Fact(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, data):
        
        self.data  = data 
        self.added = datetime.datetime.now()

        digest = md5.new(str(self.data).encode("utf-8") + \
                         str(self.added)).hexdigest()
        
        self.id = digest[0:8]

        self.cards = []


        
    ##########################################################################
    #
    # __getitem__
    #
    ##########################################################################

    def __getitem__(self, key):
        
        try:
            return self.data[key]
        except IndexError:
            raise KeyError


        
    ##########################################################################
    #
    # __setitem__
    #
    ##########################################################################

    def __setitem__(self, key, value):
        
        self.data[key] = value


        
##############################################################################
#
# add_new_fact
#
##############################################################################

# TODO: see how to integrate this best to the class above.

def add_new_fact(data):

    f = fact(data)

    get_database().add_fact(f)
