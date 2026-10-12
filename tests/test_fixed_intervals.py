#
# test_fixed_intervals.py
#

import time
from mnemosyne_test import MnemosyneTest

HOUR = 60 * 60
DAY = 24 * HOUR


class TestFixedIntervals(MnemosyneTest):

    def _card(self, text, grade=-1):
        return self.controller().create_new_cards({"f": text, "b": "b"},
            self.card_type_with_id("1"), grade=grade, tag_names=[])[0]

    def test_is_default(self):
        assert self.scheduler().name == "Fixed intervals"

    def test_intervals(self):
        sch = self.scheduler()
        card = self._card("1")
        expected_days = [1, 3, 7, 15, 30, 60]
        for grade in range(6):
            assert sch.grade_answer(card, grade, dry_run=True) == \
                expected_days[grade] * DAY
        for grade in range(6):
            sch.grade_answer(card, grade)
            assert card.next_rep == sch.next_rep_for(grade, card.last_rep)
            # Becomes due exactly at the start of day N (day_starts_at).
            now = time.time()
            assert sch.adjusted_now(now + (expected_days[grade] - 1) * DAY
                - 2 * DAY) < card.next_rep
            assert sch.adjusted_now(now + (expected_days[grade] + 1) * DAY) \
                >= card.next_rep

    def test_no_easiness_influence(self):
        sch = self.scheduler()
        a, b = self._card("a"), self._card("b")
        a.easiness, b.easiness = 1.3, 3.0
        sch.grade_answer(a, 3)
        sch.grade_answer(b, 3)
        assert a.next_rep == b.next_rep

    def test_queue_order(self):
        sch = self.scheduler()
        db = self.database()
        cards = [self._card(str(i)) for i in range(5)]
        for c in cards:
            c.grade = 2
            c.next_rep = sch.midnight_UTC(time.time()) - 2 * DAY
        # c0: due earlier (overdue longer); c1..c4 same due time.
        cards[0].next_rep -= DAY
        cards[1].last_rep, cards[1].grade = 100, 3
        cards[2].last_rep, cards[2].grade = 300, 0   # grade 0, graded later
        cards[3].last_rep, cards[3].grade = 200, 0   # grade 0, graded first
        cards[4].last_rep, cards[4].grade = 50, 4
        for c in cards:
            db.update_card(c)
        sch.reset()
        order = [sch.next_card() for i in range(5)]
        assert order == [cards[0], cards[3], cards[2], cards[4], cards[1]]

    def test_grading_order_preserved(self):
        sch = self.scheduler()
        cards = [self._card(str(i)) for i in range(4)]
        for c in cards:
            sch.grade_answer(c, 0)
            self.database().update_card(c)
        assert len(set(c.next_rep for c in cards)) == 1
        last_reps = [c.last_rep for c in cards]
        assert last_reps == sorted(set(last_reps))
        # Pretend it is the next morning.
        sch.adjusted_now = lambda now=None: cards[0].next_rep + HOUR
        sch.reset()
        assert [sch.next_card() for i in range(4)] == cards
