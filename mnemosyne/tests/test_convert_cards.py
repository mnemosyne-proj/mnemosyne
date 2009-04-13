#
# test_convert_cards.py <Peter.Bienstman@UGent.be>
#

import os
import copy

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter

class TestConverter:

    def test(self):
        c = CardTypeConverter()
        new_cards, updated_cards, deleted_cards \
                   = c.convert(None, None, None, None)
        assert new_cards == []
        assert updated_cards == []
        assert deleted_cards == []

class TestConvertCards:

    def setup(self):
        os.system("rm -fr dot_test")
        initialise(os.path.abspath("dot_test"))        

    def test_1_to_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()
        
        fact = list(database().cards_unseen())[0].fact
        old_card = copy.deepcopy(database().cards_from_fact(fact)[0])
        
        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = card_type_by_id("2")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[])
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
        new_card_1, new_card_2 = database().cards_from_fact(fact)

        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        if new_card_1.fact_view.id == 1:
            assert new_card_1 == old_card
            assert new_card_2 != old_card
            assert new_card_2.grade == -1
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card
            assert new_card_1.grade == -1
            
        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()
        
    def test_2_to_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)

        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = card_type_by_id("1")
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"], correspondence=[],
               warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1

        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == 1:
            assert new_card == old_card_1
            assert new_card != old_card_2            
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()  

    def test_1_to_3_a(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        old_card = copy.deepcopy(database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "p"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        new_card_1, new_card_2 = database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == 1:
            assert new_card_1 == old_card
            assert new_card_2 != old_card            
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card
            
        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()
        
    def test_1_to_3_b(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("1")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        old_card = copy.deepcopy(database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        new_card_1, new_card_2 = database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == 2:
            assert new_card_1 == old_card
            assert new_card_2 != old_card
        else:
            assert new_card_2 == old_card
            assert new_card_1 != old_card            

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()
            
    def test_3_to_1_a(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = card_type_by_id("1")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == 1:
            assert new_card == old_card_1
            assert new_card != old_card_2            
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()

    def test_3_to_1_b(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": ";"}
        new_card_type = card_type_by_id("1")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == 2:
            assert new_card == old_card_1
            assert new_card != old_card_2            
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()  
            
    def test_2_to_3_a(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "t"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        new_card_1, new_card_2 = database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"
        
        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view == new.fact_view

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()

    def test_2_to_3_b(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("2")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = card_type_by_id("3")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2

        new_card_1, new_card_2 = database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view != new.fact_view
                    
        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()
            
    def test_3_to_2_a(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = card_type_by_id("2")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
        new_card_1, new_card_2 = database().cards_from_fact(fact)
        
        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view == new.fact_view

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()

    def test_3_to_2_b(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": "q"}
        new_card_type = card_type_by_id("2")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 2
        
        new_card_1, new_card_2 = database().cards_from_fact(fact)
        
        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view != new.fact_view

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()

    def test_3_clone_to_1_a(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        card_type.clone("my_3")
        card_type = card_type_by_id("3_CLONED.my_3")
        
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = card_type_by_id("1")     
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == 1:
            assert new_card == old_card_1
            assert new_card != old_card_2            
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()

    def test_3_to_1_clone_a(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")        
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = card_type_by_id("1")
        new_card_type.clone("my_1")
        new_card_type = card_type_by_id("1_CLONED.my_1")
      
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1_CLONED.my_1"
        assert new_card.fact.data["q"] == "question"
        assert new_card.fact.data["a"] == "answer"
        
        if old_card_1.fact_view.id == 1:
            assert new_card == old_card_1
            assert new_card != old_card_2 
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()
        
    def test_3_clone_to_1_clone_a(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = card_type_by_id("3")
        card_type.clone("my_3")
        card_type = card_type_by_id("3_CLONED.my_3")
        
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        ui_controller_main().file_save()

        fact = list(database().cards_unseen())[0].fact
        card_1, card_2 = database().cards_from_fact(fact)
        old_card_1 = copy.deepcopy(card_1)
        old_card_2 = copy.deepcopy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = card_type_by_id("1")
        new_card_type.clone("my_1")
        new_card_type = card_type_by_id("1_CLONED.my_1")
      
        ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_cat_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert database().fact_count() == 1
        assert database().card_count() == 1
        
        new_card = database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1_CLONED.my_1"
        
        if old_card_1.fact_view.id == 1:
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()
        
    def teardown(self):
        finalise()
