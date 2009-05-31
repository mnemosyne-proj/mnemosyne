#
# test_database_stub.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises
from mnemosyne.libmnemosyne.database import Database

class TestDatabaseStub:

    def setup(self):
        self.database = Database(None)

    @raises(NotImplementedError)
    def test_new(self):
        self.database.new("path")
        
    @raises(NotImplementedError)
    def test_save(self):
        self.database.save("path")
        
    @raises(NotImplementedError)
    def test_backup(self):
        self.database.backup()
        
    @raises(NotImplementedError)
    def test_load(self):
        self.database.load("path")
        
    @raises(NotImplementedError)
    def test_unload(self):
        self.database.unload()
        
    @raises(NotImplementedError)
    def test_is_loaded(self):
        self.database.is_loaded()
        
    @raises(NotImplementedError)
    def test_add_category(self):
        self.database.add_category(None)

    @raises(NotImplementedError)
    def test_update_category(self):
        self.database.update_category(None)
        
    @raises(NotImplementedError)
    def test_delete_category(self):
        self.database.delete_category(None)
        
    @raises(NotImplementedError)
    def test_get_or_create_category_with_name(self):
        self.database.get_or_create_category_with_name("test")
        
    @raises(NotImplementedError)
    def test_remove_category_if_unused(self):
        self.database.remove_category_if_unused(None)
        
    @raises(NotImplementedError)
    def test_add_fact(self):
        self.database.add_fact(None)
        
    @raises(NotImplementedError)
    def test_update_fact(self):
        self.database.update_fact(None)
        
    @raises(NotImplementedError)
    def test_add_card(self):
        self.database.add_card(None)
        
    @raises(NotImplementedError)
    def test_update_card(self):
        self.database.update_card(None)
        
    @raises(NotImplementedError)       
    def test_delete_fact_and_related_data(self):
        self.database.delete_fact_and_related_data(None)
        
    @raises(NotImplementedError)
    def test_delete_card(self):
        self.database.delete_card(None)

    @raises(NotImplementedError)
    def test_get_category(self):
        self.database.get_category(None)

    @raises(NotImplementedError)
    def test_get_fact(self):
        self.database.get_fact(None)

    @raises(NotImplementedError)
    def test_get_card(self):
        self.database.get_card(None)

    @raises(NotImplementedError)
    def test_set_cards_active(self):
        self.database.set_cards_active(None, None)
        
    @raises(NotImplementedError)
    def test_set_cards_in_view(self):
        self.database.set_cards_in_view(None, None)
        
    @raises(NotImplementedError)
    def test_category_names(self):
        self.database.category_names()
           
    @raises(NotImplementedError)       
    def test_cards_from_fact(self):        
        self.database.cards_from_fact(None)

    @raises(NotImplementedError)
    def test_has_fact_with_data(self):
        self.database.has_fact_with_data(None, None)

    @raises(NotImplementedError)
    def test_duplicates_for_fact(self):
        self.database.duplicates_for_fact(None)

    @raises(NotImplementedError)
    def test_fact_count(self):
        self.database.fact_count()

    @raises(NotImplementedError)
    def test_card_count(self):
        self.database.card_count()

    @raises(NotImplementedError)
    def test_non_memorised_count(self):
        self.database.non_memorised_count()

    @raises(NotImplementedError)
    def test_scheduled_count(self):
        self.database.scheduled_count(0)

    @raises(NotImplementedError)
    def test_active_count(self):
        self.database.active_count()

    @raises(NotImplementedError)
    def test_average_easiness(self):
        self.database.average_easiness()

    @raises(NotImplementedError)
    def test_card_types_in_use(self):
        self.database.card_types_in_use()

    @raises(NotImplementedError)
    def test_cards_due_for_ret_rep(self):
        self.database.cards_due_for_ret_rep()

    @raises(NotImplementedError)
    def test_cards_due_for_final_review(self):
        self.database.cards_due_for_final_review(2)

    @raises(NotImplementedError)
    def test_cards_new_memorising(self):
        self.database.cards_new_memorising(1)

    @raises(NotImplementedError)
    def test_cards_unseen(self):
        self.database.cards_unseen(2)
        
    @raises(NotImplementedError)   
    def test_cards_learn_ahead(self):
        self.database.cards_learn_ahead()
