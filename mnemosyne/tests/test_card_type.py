#
# test_card_type.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class DecoratedThreeSided(CardType):

    id = "3_decorated"
    name = "Foreign word with pronunciation (decorated)"
    
    # List and name the keys.
    fields = [("f", "Foreign word", None),
              ("p", "Pronunciation", None),
              ("t", "Translation", None)]

    # Recognition.
    v1 = FactView("Recognition", "3::1")
    v1.q_fields = ["f"]
    v1.a_fields = ["p", "t"]
    v1.q_field_decorators = {"f": "What is the translation of ${f}?"}
    
    # Production.
    v2 = FactView("Production", "3::2")
    v2.q_fields = ["t"]
    v2.a_fields = ["f", "p"]
    v2.q_field_decorators = {"t": "How do you say ${t}?"}
    
    fact_views = [v1, v2]
    unique_fields = ["f"]
    required_fields = ["f", "t"]
    
class TestCardType(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne(upload_science_logs=False)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_card_type", "DecoratedThreeSided"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

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
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().card_type(card_type.id,
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

        card_type_out = self.database().card_type(card_type_2.id,
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
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().card_type(card_type.id,
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

    def test_decorators(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = self.card_type_by_id("3_decorated")
        card = self.controller().create_new_cards(fact_data, card_type,
                  grade=-1, tag_names=["default"])[0]
        assert "What is the translation of foreign word?" in card.question()
