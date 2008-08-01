##############################################################################
#
# fact.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import datetime, md5



##############################################################################
#
# Fact
#
#   Basic unit of information from which several cards can be derived.
#   The fields are stored in a dictionary.
#
# TODO: make list of common keys for standardisation.
#
##############################################################################

class Fact(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, data, id=None):
        
        self.data  = data 
        self.added = datetime.datetime.now()

        if id is not None:

            digest = md5.new(str(self.data).encode("utf-8") + \
                             str(self.added)).hexdigest()
            
            id = digest[0:8]
        
        self.id = id


        
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

        
