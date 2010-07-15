#
# test_card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest

class TestCardType(MnemosyneTest):

    def test_card_types(self):
        card_type = self.card_type_by_id("1")
        assert card_type.key_with_name("Question") == "q"
        assert card_type.is_data_valid({"q": "foo"}) == True
        assert self.card_type_by_id("1") == self.card_type_by_id("1")
        assert self.card_type_by_id("1") != None        

    def test_database(self):
        card_type = self.card_type_by_id("1")
        card_type.fact_views[0].type_answer = True
        card_type.fact_views[0].extra_data = {"a": "b"}        
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        card_type.extra_data = {"b": "b"}
        self.database().update_card_type(card_type)
        self.database().save()
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().get_card_type(card_type.id,
                                                      id_is_internal=False)
        assert card_type_out.key_with_name("Question") == "q"
        assert card_type_out.required_fields == ["q"]
        assert card_type_out.is_data_valid({"q": "foo"}) == True

        assert card_type_out.fields == card_type.fields
        assert card_type_out.unique_fields == card_type.unique_fields
        assert card_type_out.keyboard_shortcuts == card_type.keyboard_shortcuts
        assert card_type_out.fact_views[0].type_answer == True
        assert card_type_out.fact_views[0].extra_data == {"a": "b"}
        assert card_type_out.extra_data == {"b": "b"}
        assert len(card_type.fact_views) == 1                                
        assert len(card_type_out.fact_views) == 1
        assert card_type_out.fact_views[0].id == \
               card_type.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type.fact_views[0].name
        assert card_type_out.fact_views[0].q_fields == \
               card_type.fact_views[0].q_fields
        assert card_type_out.fact_views[0].a_fields == \
               card_type.fact_views[0].a_fields
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type.fact_views[0].a_on_top_of_q
        
        # Reset global variables.
        card_type.fact_views[0].type_answer = False
        card_type.fact_views[0].extra_data = {}
        
    def test_delete(self):
        card_type = self.card_type_by_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_by_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")

        self.controller().delete_card_type(card_type_1)

        card_type_out = self.database().get_card_type(card_type_2.id,
                                                      id_is_internal=False)

        assert card_type_out.fact_views[0].id == \
               card_type.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type.fact_views[0].name
        assert card_type_out.fact_views[0].q_fields == \
               card_type.fact_views[0].q_fields
        assert card_type_out.fact_views[0].a_fields == \
               card_type.fact_views[0].a_fields
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type.fact_views[0].a_on_top_of_q        
        
    def test_clone_of_clone(self):
        card_type = self.card_type_by_id("1")
        card_type.fact_views[0].type_answer = True
        card_type.fact_views[0].extra_data = {"a": "b"}        
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        card_type.extra_data = {"b": "b"}
        self.database().update_card_type(card_type)
        self.database().save()
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().get_card_type(card_type.id,
                                                      id_is_internal=False)
        assert card_type_out.key_with_name("Question") == "q"
        assert card_type_out.required_fields == ["q"]
        assert card_type_out.is_data_valid({"q": "foo"}) == True

        assert card_type_out.fields == card_type.fields
        assert card_type_out.unique_fields == card_type.unique_fields
        assert card_type_out.keyboard_shortcuts == card_type.keyboard_shortcuts
        assert card_type_out.fact_views[0].type_answer == True
        assert card_type_out.fact_views[0].extra_data == {"a": "b"}
        assert card_type_out.extra_data == {"b": "b"}
        assert len(card_type.fact_views) == 1                                
        assert len(card_type_out.fact_views) == 1
        assert card_type_out.fact_views[0].id == \
               card_type.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type.fact_views[0].name
        assert card_type_out.fact_views[0].q_fields == \
               card_type.fact_views[0].q_fields
        assert card_type_out.fact_views[0].a_fields == \
               card_type.fact_views[0].a_fields
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type.fact_views[0].a_on_top_of_q

        # Reset global variables.
        card_type.fact_views[0].type_answer = False
        card_type.fact_views[0].extra_data = {}   
