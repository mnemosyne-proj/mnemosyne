#
# test_statistics.py <Peter.Bienstman@UGent.be>
#

import os
import datetime

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.loggers.science_log_parser import ScienceLogParser


class TestStatistics(MnemosyneTest):

    def test_current_card(self):
        from mnemosyne.libmnemosyne.statistics_pages.current_card import CurrentCard
        page = CurrentCard(self.mnemosyne.component_manager)
        page.prepare_statistics(0)
        assert "No current card." in page.html       
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().new_question()
        page.prepare_statistics(0)
        assert "Unseen card, no statistics available yet." in page.html      
        self.review_controller().grade_answer(1)
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
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().new_question()
        self.review_controller().grade_answer(1)
        page = Easiness(self.mnemosyne.component_manager)
        
        page.prepare_statistics(-1)
        assert page.data == [2.5]
        page.prepare_statistics(page.variants[1][0])
        assert page.data == [2.5]

    def test_past_schedule(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_mem_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "schedule_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        days_elapsed = datetime.date.today() - datetime.date(2009, 8, 15)
        assert self.scheduler().card_count_scheduled_n_days_from_now(\
            -days_elapsed.days) == 124
        assert self.scheduler().card_count_scheduled_n_days_from_now(-1) == 0

    def test_schedule_page(self):
        from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
        page = Schedule(self.mnemosyne.component_manager)
        for i in range(1, 7):
            page.prepare_statistics(i)

    @raises(AttributeError)
    def test_schedule_page_2(self):
        from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
        page = Schedule(self.mnemosyne.component_manager)
        page.prepare_statistics(8)

    def test_added_cards(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_mem_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "added_1.txt")
        ScienceLogParser(self.database()).parse(filename)
        days_elapsed = datetime.date.today() - datetime.date(2009, 8, 19)
        assert self.database().card_count_added_n_days_ago(days_elapsed.days) \
               == 2
        assert self.scheduler().card_count_scheduled_n_days_from_now(1) == 0
        
    def test_added_cards_page(self):
        from mnemosyne.libmnemosyne.statistics_pages.cards_added import CardsAdded
        page = CardsAdded(self.mnemosyne.component_manager)
        for i in range(1, 4):
            page.prepare_statistics(i)
            
    @raises(AttributeError)
    def test_added_cards_page_2(self):
        from mnemosyne.libmnemosyne.statistics_pages.cards_added import CardsAdded
        page = CardsAdded(self.mnemosyne.component_manager)
        page.prepare_statistics(0)

    def test_score(self):
        self.database().update_card_after_log_import = (lambda x, y, z: 0)
        self.database().before_mem_import()
        filename = os.path.join(os.getcwd(), "tests", "files", "score_1.txt")        
        ScienceLogParser(self.database()).parse(filename)
        days_elapsed = datetime.date.today() - datetime.date(2009, 8, 17)
        assert self.database().retention_score_n_days_ago(days_elapsed.days) \
               == 5/7.*100
        assert self.database().retention_score_n_days_ago(0) == 0
        from mnemosyne.libmnemosyne.statistics_pages.retention_score import RetentionScore
        page = RetentionScore(self.mnemosyne.component_manager)
        page.prepare_statistics(1)
        page.prepare_statistics(2)
        page.prepare_statistics(3)
                
    @raises(AttributeError)
    def test_score_page(self):
        from mnemosyne.libmnemosyne.statistics_pages.retention_score import RetentionScore
        page = RetentionScore(self.mnemosyne.component_manager)
        page.prepare_statistics(0)
        
