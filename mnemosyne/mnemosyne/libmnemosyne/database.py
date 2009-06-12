#
# database.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Database(Component):

    """Interface class describing the functions to be implemented by the
    actual database classes.

    """

    version = ""
    component_type = "database"

    def deactivate(self):
        self.unload()

    # Creating, loading and saving the entire database.

    def new(self, path):
        raise NotImplementedError

    def save(self, path=None):
        raise NotImplementedError

    def backup(self):
        raise NotImplementedError

    def load(self, path):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def is_loaded(self):
        raise NotImplementedError

    # Adding, modifying and deleting categories, facts and cards.

    def add_category(self, category):
        raise NotImplementedError

    def update_category(self, category):
        raise NotImplementedError

    def delete_category(self, category):
        raise NotImplementedError

    def get_or_create_category_with_name(self, name):
        raise NotImplementedError

    def remove_category_if_unused(self, category):
        raise NotImplementedError

    def add_fact(self, fact):
        raise NotImplementedError

    def update_fact(self, fact):
        raise NotImplementedError

    def add_card(self, card):
        raise NotImplementedError

    def update_card(self, card, repetition_only=False):
        raise NotImplementedError
        
    def delete_fact_and_related_data(self, fact):
        raise NotImplementedError

    def delete_card(self, card):
        raise NotImplementedError
    
    # Retrieving categories, facts, cards using their internal id.
    
    def get_category(self, _id):
        raise NotImplementedError
    
    def get_fact(self, _id):
        raise NotImplementedError

    def get_card(self, _id):
        raise NotImplementedError
    
    # Activate or put cards in view.

    def set_cards_active(self, card_types_fact_views, categories):

        """ card_types_fact_views is a list of tuples containing (card_type,
        fact_view).

        """
        
        raise NotImplementedError

    def set_cards_in_view(self, card_types_fact_views, categories):

        """ card_types_fact_views is a list of tuples containing (card_type,
        fact_view).

        """
        
        raise NotImplementedError    
    
    # Queries.

    def category_names(self):
        raise NotImplementedError

    def cards_from_fact(self, fact):
        
        """ Returns a list of the cards deriving from a fact. """
        
        raise NotImplementedError

    def has_fact_with_data(self, fact_data, card_type):
        raise NotImplementedError
    
    def count_related_cards_with_next_rep(self, card, next_rep):

        """Returns how many related cards with grade >= 2 are scheduled at
        'next_rep'. Note that there is no need that next_rep == card.next_rep.

        """
        
        raise NotImplementedError        

    def duplicates_for_fact(self, fact):

        """Returns list of facts which have the same unique key."""

        raise NotImplementedError

    def card_types_in_use(self):
        raise NotImplementedError

    def fact_count(self):
        raise NotImplementedError

    def card_count(self):
        raise NotImplementedError

    def non_memorised_count(self):
        raise NotImplementedError

    def scheduled_count(self, days=0):
        raise NotImplementedError

    def active_count(self):
        raise NotImplementedError

    def average_easiness(self):
        raise NotImplementedError

    # Card queries used by the scheduler. Returns tuples of internal ids
    # (_card_id, _fact_id) Should function as an iterator in order to save
    # memory. "sort_key" is a string of an attribute of Card to be used for
    # sorting, with "" standing for the order in which the cards where added
    # (no sorting), and "random" is used to shuffle the cards. "limit" is
    # used to limit the number of cards returned by the iterator, with -1
    # meaning no limit.
    
    def cards_due_for_ret_rep(self, now, sort_key="", limit=-1):
        raise NotImplementedError

    def cards_due_for_final_review(self, grade, sort_key="", limit=-1):
        raise NotImplementedError

    def cards_new_memorising(self, grade, sort_key="", limit=-1):
        raise NotImplementedError

    def cards_unseen(self, sort_key="", limit=-1):
        raise NotImplementedError
    
    def cards_learn_ahead(self, now, sort_key="", limit=-1):
        raise NotImplementedError

    # Extra commands for custom schedulers.
    
    def set_scheduler_data(self, scheduler_data):
        raise NotImplementedError

    def cards_with_scheduler_data(self, scheduler_data, sort_key="", limit=-1):
        raise NotImplementedError

    def scheduler_data_count(self, scheduler_data):        
        raise NotImplementedError
