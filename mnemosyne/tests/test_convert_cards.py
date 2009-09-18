#
# test_convert_cards.py <Peter.Bienstman@UGent.be>
#

import os
import copy

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):

    def question_box(self, question, option0, option1, option2):
        if option0 == "&Proceed and delete":
            return 0
        if option0 == "&OK": # Reset learning history
            return 0
        raise NotImplementedError


class TestConverter:

    def test(self):
        c = CardTypeConverter(None)
        new_cards, updated_cards, deleted_cards \
                   = c.convert(None, None, None, None)
        assert new_cards == []
        assert updated_cards == []
        assert deleted_cards == []

class TestConvertCards(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_convert_cards", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))
        self.review_controller().reset()
            
    def test_1_to_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()
        
        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
        
        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = self.card_type_by_id("2")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card_1, new_card_2 = self.database().cards_from_fact(fact)

        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        if new_card_1.fact_view.id == "2::1":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)

        new_fact_data = {"q": "question2",                    
                         "a": "answer2"}
        new_card_type = self.card_type_by_id("1")
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "2::1":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "p"}
        new_card_type = self.card_type_by_id("3")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == "3::1":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        old_card = copy.copy(self.database().cards_from_fact(fact)[0])
                
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = self.card_type_by_id("3")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        assert new_card_1.fact.card_type.id == "3"
        assert new_card_2.fact.card_type.id == "3"

        if new_card_1.fact_view.id == "3::2":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("1")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "3::1":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": ";"}
        new_card_type = self.card_type_by_id("1")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "3::2":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "f", "a": "t"}
        new_card_type = self.card_type_by_id("3")     
        self.controller().update_related_cards(fact, new_fact_data,
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
                    assert old.fact_view.id.split("::")[1] == \
                           new.fact_view.id.split("::")[1]

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()

    def test_2_to_3_b(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("2")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"f": "foreign word",
                         "p": "pronunciation",
                         "t": "translation"}
        correspondence = {"q": "t", "a": "f"}
        new_card_type = self.card_type_by_id("3")     
        self.controller().update_related_cards(fact, new_fact_data,
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("2")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card_1, new_card_2 = self.database().cards_from_fact(fact)
        
        assert new_card_1.fact.card_type.id == "2"
        assert new_card_2.fact.card_type.id == "2"

        for old in [old_card_1, old_card_2]:
            for new in [new_card_1, new_card_2]:
                if old == new:
                    assert old.fact_view.id.split("::")[1] == \
                           new.fact_view.id.split("::")[1]

        new_card_1.question()
        new_card_1.answer()        
        new_card_2.question()
        new_card_2.answer()

    def test_3_to_2_b(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = self.card_type_by_id("3")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "a", "t": "q"}
        new_card_type = self.card_type_by_id("2")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
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
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_by_id("3::my_3")
        
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}
        new_card_type = self.card_type_by_id("1")     
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1"
        
        if old_card_1.fact_view.id == "3::1":
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
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = self.card_type_by_id("1")
        self.controller().clone_card_type(new_card_type, "my_1")
        new_card_type = self.card_type_by_id("1::my_1")
      
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1::my_1"
        assert new_card.fact.data["q"] == "question"
        assert new_card.fact.data["a"] == "answer"
        
        if old_card_1.fact_view.id == "3::1":
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
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_by_id("3::my_3")
        
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()

        fact = card.fact
        card_1, card_2 = self.database().cards_from_fact(fact)
        old_card_1 = copy.copy(card_1)
        old_card_2 = copy.copy(card_2)
        
        new_fact_data = {"q": "question",
                         "a": "answer"}
        correspondence = {"f": "q", "t": "a"}      
        new_card_type = self.card_type_by_id("1")
        self.controller().clone_card_type(new_card_type, "my_1")
        new_card_type = self.card_type_by_id("1::my_1")
      
        self.controller().update_related_cards(fact, new_fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence=correspondence)
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
        new_card = self.database().cards_from_fact(fact)[0]
        assert new_card.fact.card_type.id == "1::my_1"
        
        if old_card_1.fact_view.id == "3::1":
            assert new_card == old_card_1
            assert new_card != old_card_2
        else:
            assert new_card == old_card_2
            assert new_card != old_card_1
            
        new_card.question()
        new_card.answer()

    def test_cloze_to_1(self):
        from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
             StatisticsWidget
        from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
        class ScheduleWdgt(StatisticsWidget):
            used_for = Schedule
        self.mnemosyne.component_manager.register(ScheduleWdgt)
    
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "5":
                plugin.activate()
                
        fact_data = {"text": "[question]"}
        card_type = self.card_type_by_id("5")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        self.controller().file_save()
        self.review_controller().reset()
        print self.review_controller().card

        new_card_type = self.card_type_by_id("1")
        fact_data = {"q": "[question]", "a": ""}
        self.controller().update_related_cards(card.fact, fact_data,
               new_card_type, new_tag_names=["default2"],
               correspondence={'text': 'q'})

        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        new_card = self.database().cards_from_fact(card.fact)[0]
        
        new_card.question()
        new_card.answer()          

    def test_2_to_2_clone(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("2")        
        card_1, card_2  = self.controller().create_new_cards(fact_data,
                                 card_type, grade=-1, tag_names=["default"])
        self.controller().file_save()
        
        new_card_type = self.controller().\
                        clone_card_type(card_type, "my_2")
      
        self.controller().update_related_cards(card_1.fact, fact_data,
               new_card_type, new_tag_names=["default"],
               correspondence={})
        
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
        new_card = self.database().cards_from_fact(card_1.fact)[0]
        assert new_card.fact.card_type.id == "2::my_2"
        assert new_card.fact.data["q"] == "question"
        assert new_card.fact.data["a"] == "answer"

        new_card.question()
        new_card.answer()
