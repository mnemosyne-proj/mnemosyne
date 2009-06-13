#
# test_add_cards.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestAddCards(MnemosyneTest):

    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1

        assert self.database().average_easiness() == 2.5

    def test_1_duplicates(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])
        self.ui_controller_main().file_save()
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"],
                                              warn=False)
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 1
        
    def test_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("2")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2
        
    def test_3(self):
        fact_data = {"f": "foreign word",
                     "p": "pronunciation",
                     "t": "translation"}
        card_type = self.card_type_by_id("3")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])
        self.ui_controller_main().file_save()
        assert self.database().fact_count() == 1
        assert self.database().card_count() == 2

    def test_delete(self):
        fact_data = {"q": "question1",
                     "a": "answer1"}
        card_type = self.card_type_by_id("1")
        card_1 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, tag_names=["default"])[0]
        fact_data = {"q": "question2",
                     "a": "answer2"}
        card_2 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, tag_names=["default"])[0]
        assert set(tag.name for tag in card_1.tags) == \
               set(tag.name for tag in card_2.tags)
        fact_data = {"q": "question3",
                     "a": "answer3"}
        card_3 = self.ui_controller_main().create_new_cards(fact_data, card_type,
                              warn=False, grade=0, tag_names=["default"])[0]
        self.ui_controller_review().new_question()
        assert self.ui_controller_review().card == card_1
        self.ui_controller_review().grade_answer(0)
        self.database().delete_fact_and_related_data(card_3.fact)
        self.ui_controller_review().rebuild_queue()
        self.ui_controller_review().new_question() 
        for i in range(6):
            assert self.ui_controller_review().card != card_3
            self.ui_controller_review().grade_answer(0)        

    def test_change_tag(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, tag_names=["default"])[0]
        self.ui_controller_review().new_question()
        self.ui_controller_main().update_related_cards(card.fact, fact_data, \
            card_type, ["new"], correspondence={}, warn=False)     
        new_card = self.database().get_card(card._id)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "new" in tag_names
