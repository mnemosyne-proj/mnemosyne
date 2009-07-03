#
# test_statistics.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestStatistics(MnemosyneTest):

    def test_current_card(self):
        from mnemosyne.libmnemosyne.statistics_pages.current_card import CurrentCard
        page = CurrentCard(self.mnemosyne.component_manager)
        page.prepare_statistics(0)
        assert "No current card." in page.html       
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.ui_controller_main().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.ui_controller_review().new_question()
        page.prepare_statistics(0)
        assert "Unseen card, no statistics available yet." in page.html      
        self.ui_controller_review().grade_answer(1)
        page.prepare_statistics(0)
        assert "No current card." not in page.html
        assert "Unseen card, no statistics available yet." not in page.html
        
    def test_easiness(self):
        from mnemosyne.libmnemosyne.statistics_pages.easiness import Easiness
        page = Easiness(self.mnemosyne.component_manager)
        page.prepare_statistics(-1)
        assert len(page.data) == 0
        
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.ui_controller_main().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.ui_controller_review().new_question()
        self.ui_controller_review().grade_answer(1)
        page = Easiness(self.mnemosyne.component_manager)
        
        page.prepare_statistics(-1)
        print page.data
        assert page.data == [2.5]
        page.prepare_statistics(page.variants[1][0])
        print page.data
        assert page.data == [2.5]   
