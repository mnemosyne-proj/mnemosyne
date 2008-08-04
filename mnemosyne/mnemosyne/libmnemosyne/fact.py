##############################################################################
#
# fact.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import datetime, md5

from mnemosyne.libmnemosyne.plugin_manager import get_database,



##############################################################################
#
# Fact
#
#   Basic unit of information from which several cards can be derived.
#   The fields are stored in a dictionary.
#
#   Categories and card_type_id are stored here, because when resetting the
#   learning data on export, we only export facts. Of course cards can have
#   categories of their own as well.
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

    def __init__(self, data, cat_names, card_type_id, id=None):

        self.added = datetime.datetime.now()
        
        self.data         = data 
        self.categories   = categories
        self.card_type_id = card_type_id

        self.cat = []
        for cat_name in cat_names:
            self.cat.append(db.get_or_create_category_with_name(cat_name))

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


    ##########################################################################
    #
    # is_active
    #
    ##########################################################################

    def is_active(self):
        
        for c in self.cat:
            if c.active == False:
                return False
            
        return True

        
