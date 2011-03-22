#
# database.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Database(Component):

    """Interface class describing the functions to be implemented by the
    actual database classes.

    Apart from the basic interface defined here, depending on the situation
    a database can also implement functions for logging, statistics and
    syncing (see SQLite_logging.py, SQLite_statistics.py, SQLite_sync.py).

    """

    version = ""
    default_name = "default"  # Without suffix, should not be translated.
    suffix = ""
    component_type = "database"

    def deactivate(self):
        self.unload()

    def path(self):

        """Returns full path of the database."""
        
        raise NotImplementedError
        
    def name(self):

        """Returns name of the database, without parent paths, but with
        extensions.

        """
        
        raise NotImplementedError
    
    def display_name(self):

        """Returns bare name of the database, without parent paths and
        without extension.

        """
        
        raise NotImplementedError
        
    # File operations.

    def release_connection(self):

        """Release the connection, so that it may be recreated in a separate
        thread.

        """

    def new(self, path):
        raise NotImplementedError       

    def save(self, path=None):
        raise NotImplementedError

    def backup(self):
        raise NotImplementedError

    def restore(self, path):
        raise NotImplementedError        

    def load(self, path):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def abandon(self):
        raise NotImplementedError        

    def is_loaded(self):
        raise NotImplementedError
    
    def is_empty(self):
        raise NotImplementedError

    # Functions to conform to openSM2sync API.

    def user_id(self):
        return self.config()["user_id"]

    def set_user_id(self, user_id):
        self.config().change_user_id(user_id)
    
    # Tags.

    def add_tag(self, tag):
        raise NotImplementedError

    def tag(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_tag(self, tag):
        raise NotImplementedError

    def delete_tag(self, tag):
        raise NotImplementedError

    def get_or_create_tag_with_name(self, name):
        raise NotImplementedError
    
    def get_or_create_tags_with_names(self, names):
        raise NotImplementedError
    
    def delete_tag_if_unused(self, tag):
        raise NotImplementedError

    def tags(self):        
        raise NotImplementedError        
    
    # Facts.
    
    def add_fact(self, fact):
        raise NotImplementedError
    
    def fact(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_fact(self, fact):
        raise NotImplementedError

    def delete_fact(self, fact):
        raise NotImplementedError
    
    # Cards.
    
    def add_card(self, card):
        raise NotImplementedError
        
    def card(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_card(self, card, repetition_only=False):
        raise NotImplementedError

    def delete_card(self, card):
        raise NotImplementedError
    
    # Fact views.
    
    def add_fact_view(self, fact_view):
        raise NotImplementedError

    def fact_view(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_fact_view(self, fact_view):
        raise NotImplementedError

    def delete_fact_view(self, fact_view):
        raise NotImplementedError
    
    # Card types.
    
    def add_card_type(self, card_type):
        raise NotImplementedError

    def card_type(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_card_type(self, card_type):
        raise NotImplementedError

    def delete_card_type(self, card_type):
        raise NotImplementedError

    # Criteria.
    
    def add_criterion(self, criterion):
        raise NotImplementedError

    def criterion(self, id, is_id_internal):
        raise NotImplementedError
    
    def update_criterion(self, criterion):
        raise NotImplementedError

    def delete_criterion(self, criterion):
        raise NotImplementedError
    
    def set_current_criterion(self, criterion):
        raise NotImplementedError        
    
    def current_criterion(self):
        raise NotImplementedError
    
    def criteria(self):
        raise NotImplementedError    
    
    # Queries.

    def cards_from_fact(self, fact):
        
        """Return a list of the cards deriving from a fact."""
        
        raise NotImplementedError     

    def duplicates_for_fact(self, fact, card_type):

        """Return facts with same 'card_type.unique_fields' data as 'fact'."""

        raise NotImplementedError

    def card_types_in_use(self):
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