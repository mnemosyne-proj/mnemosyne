#
# database.py <Peter.Bienstman@UGent.be>
#

from component import Component


#  TODO: load_failed mechanism, to prevent overwriting a database which
#  failed to load.

class Database(Component):

    """Interface class describing the functions to be implemented by the
    actual database classes.

    """

    # Creating, loading and saving the entire database.

    def new(self, path):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def backup(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def is_loaded():
        raise NotImplementedError

    # Start date.

    def set_start_date(self, start_date_obj):
        raise NotImplementedError

    def days_since_start(self):
        raise NotImplementedError

    # Adding, modifying and deleting categories, facts and cards.

    # TODO: join add and modify into save?

    def add_category(self, category):
        raise NotImplementedError

    def modify_category(self, id, modified_category):
        raise NotImplementedError

    def delete_category(self, category):
        raise NotImplementedError

    def get_or_create_category_with_name(self, name):
        raise NotImplementedError

    def remove_category_if_unused(self, cat):
        raise NotImplementedError

    def add_fact(self, fact):
        raise NotImplementedError

    def modify_fact(self, id, modified_fact):
        raise NotImplementedError

    def delete_fact(self, fact):
        raise NotImplementedError

    def add_card(self, card): # should also link fact to new card
        raise NotImplementedError

    def modify_card(self, id, modified_card):
        raise NotImplementedError

    def delete_card(self, id, card):
        raise NotImplementedError

    # Queries. TODO: check which ones we need more.

    def fact(self, id):
        raise NotImplementedError

    def card(self, id):
        raise NotImplementedError

    def fact_count(self):
        raise NotImplementedError

    def card_count(self):
        raise NotImplementedError

    def non_memorised_count(self):
        raise NotImplementedError

    def scheduled_count(self):
        raise NotImplementedError

    def active_count(self):
        raise NotImplementedError

    def average_easiness(self):
        raise NotImplementedError

    # Filter is a SQL filter, used e.g. to filter out inactive categories.

    def set_filter(self, filter):
        raise NotImplementedError

    # The following functions should return an iterator, in order to save memory.

    def cards_due_for_ret_rep(self, sort_key=None):
        raise NotImplementedError

    def cards_due_for_final_review(self, grade, sort_key=None):
        raise NotImplementedError

    def cards_new_memorising(self, grade, sort_key=None):
        raise NotImplementedError

    def cards_unseen(self, sort_key=None):
        raise NotImplementedError
