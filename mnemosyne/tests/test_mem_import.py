#
# test_mem_import.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne


class TestMemImport(MnemosyneTest):

    def get_mem_importer(self):
        for format in self.mnemosyne.component_manager.get_all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                return format

    def test_card_type_1(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.grade == 2
        assert card.easiness == 2.5
        assert card.acq_reps == 1
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 1
        assert card.ret_reps_since_lapse == 0
        assert [tag.name for tag in card.tags] == ["<default>"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"
        
    def test_card_type_1_unseen(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "1sided_unseen.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card = self.review_controller().card
        assert card.grade == -1
        assert card.easiness == 2.5
        assert card.acq_reps == 0
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 0
        assert card.ret_reps_since_lapse == 0
        assert card.last_rep == -1
        assert card.next_rep == -1
        
    def test_card_type_2(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "2sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert "question" in card_1.question()
        assert "answer" in card_1.answer()        
        cards = self.database().cards_from_fact(card_1.fact)
        if cards[0] == card_1:
            card_2 = cards[1]
        else:
            card_2 = cards[0]
        assert "question" in card_2.answer()
        assert "answer" in card_2.question()
        
    def test_card_type_3(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p": "p", "t": "t"}

    def test_card_type_3_corrupt(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_corrupt.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 2
        card_1 = self.review_controller().card
        assert card_1.fact.data == {"f": "f", "p": "", "t": "t"}
        
    def test_card_type_3_missing(self):
        filename = os.path.join(os.getcwd(), "tests", "files", "3sided_missing.mem")
        self.get_mem_importer().do_import(filename)
        self.review_controller().reset()
        assert self.database().card_count() == 1
        card_1 = self.review_controller().card
        print card_1.fact.data
        assert card_1.fact.data == {"q": "t", "a": "f\np"}
