#
# test_convert_cards.py <Peter.Bienstman@UGent.be>
#

import copy

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter

class TestConverter:

    def test(self):
        c = CardTypeConverter(None)
        new_cards, updated_cards, deleted_cards \
                   = c.convert(None, None, None, None)
        assert new_cards == []
        assert updated_cards == []
        assert deleted_cards == []

class TestConvertCards(MnemosyneTest):

    def test_1_to_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()
        
        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
        
        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = self.card_type_by_id("2")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        if new_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("2")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = self.card_type_by_id("1")
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[],
               warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "p"}
        new_card_type = self.card_type_by_id("3")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = self.card_type_by_id("3")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == "2":
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
        card_type = self.card_type_by_id("3")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("1")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("3")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": ";"}
        new_card_type = self.card_type_by_id("1")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "2":
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
        card_type = self.card_type_by_id("2")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "t"}
        new_card_type = self.card_type_by_id("3")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
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
        card_type = self.card_type_by_id("2")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = self.card_type_by_id("3")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
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
        card_type = self.card_type_by_id("3")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("2")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        
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
        card_type = self.card_type_by_id("3")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": "q"}
        new_card_type = self.card_type_by_id("2")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        
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
        card_type = self.card_type_by_id("3")
        card_type.clone("my_3")
        card_type = self.card_type_by_id("3_CLONED.my_3")
        
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("1")     
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("3")        
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = self.card_type_by_id("1")
        new_card_type.clone("my_1")
        new_card_type = self.card_type_by_id("1_CLONED.my_1")
      
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1_CLONED.my_1"
        assert new_card.fact.data["q"] == "question"
        assert new_card.fact.data["a"] == "answer"
        
        if old_card_1.fact_view.id == "1":
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
        card_type = self.card_type_by_id("3")
        card_type.clone("my_3")
        card_type = self.card_type_by_id("3_CLONED.my_3")
        
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.ui_controller_main().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = self.card_type_by_id("1")
        new_card_type.clone("my_1")
        new_card_type = self.card_type_by_id("1_CLONED.my_1")
      
        self.ui_controller_main().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence, warn=False)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1_CLONED.my_1"
        
        if old_card_1.fact_view.id == "1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()
