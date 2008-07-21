##############################################################################
#
# database.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# Database
#
#  TODO: perhaps we need to break out a FactManager and a CardManager
#  from this code.
#
##############################################################################

class Database(Plugin):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, widget,
                 name, description, can_be_unregistered=True):

        self.type                = "batabase"
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered


        
    ##########################################################################
    #
    # Functions to be implemented by the actual database.
    #
    ##########################################################################
    
    # Creating, loading and saving the entire database.

    def new(self, name):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
    
    def backup(self):
        raise NotImplementedError
    
    def load(self):
        raise NotImplementedError

    # Start date.

    def save_start_date(self):
        raise NotImplementedError

    def load_start_date(self):
        raise NotImplementedError

    # Adding, modifying and deleting facts and cards.

    def add_fact(self, fact):
        raise NotImplementedError

    def modify_fact(self, id, modified_fact)
        raise NotImplementedError
    
    def delete_fact(self, fact)
        raise NotImplementedError
    
    def add_card(self, card): # should also link fact to new card
        raise NotImplementedError

    def modify_card(self, id, modified_card)
        raise NotImplementedError
    
    def delete_card(self, id, card)
        raise NotImplementedError
    
    # Queries. TODO: check which ones we need more.
    
    def get_fact(self, id):
        raise NotImplementedError
    
    def get_card(self, id):
        raise NotImplementedError        

    def count_facts(self):
        raise NotImplementedError

    def count_count(self):
        raise NotImplementedError

    def count_non_memorised(self):
        raise NotImplementedError
    
    def count_scheduled(self):
        raise NotImplementedError

    def count_active(self):
        raise NotImplementedError
    
    def average_easiness(self):
        raise NotImplementedError        
    
    def cards_due_for_acq_rep(self):
        raise NotImplementedError
