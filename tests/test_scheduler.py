#
# test_scheduler.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time
import datetime
import calendar
from mnemosyne_test import MnemosyneTest

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


class TestScheduler(MnemosyneTest):

    def test_midnight_UTC(self):
        if sys.platform == "win32":
            return  # no time.tzset
        sch = self.scheduler()
        os.environ["TZ"] = "UTC"
        time.tzset()
        midnight_UTC = int(time.mktime(datetime.datetime(2012,1,14,0,0,0).timetuple()))

        os.environ["TZ"] = "Australia/Sydney"
        time.tzset()
        t = time.mktime(datetime.datetime(2012,1,14,0,0,0).timetuple())
        assert sch.midnight_UTC(t) == midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,2,0,0).timetuple())
        assert sch.midnight_UTC(t) == midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,23,59,0).timetuple())
        assert sch.midnight_UTC(t) == midnight_UTC

        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()
        t = time.mktime(datetime.datetime(2012,1,14,0,0,0).timetuple())
        assert sch.midnight_UTC(t) == midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,23,59,0).timetuple())
        assert sch.midnight_UTC(t) == midnight_UTC

    def test_adjusted_now(self):
        if sys.platform == "win32":
            return  # no time.tzset
        sch = self.scheduler()
        os.environ["TZ"] = "UTC"
        time.tzset()
        midnight_UTC = int(time.mktime(datetime.datetime(2012,1,14,0,0,0).timetuple()))

        os.environ["TZ"] = "Europe/Brussels"
        time.tzset()
        t = time.mktime(datetime.datetime(2012,1,14,2,59,0).timetuple())
        assert sch.adjusted_now(t) < midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,3,0,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC

        os.environ["TZ"] = "Australia/Sydney"
        time.tzset()
        t = time.mktime(datetime.datetime(2012,1,14,2,59,0).timetuple())
        t0 = t
        assert sch.adjusted_now(t) < midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,3,0,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,15,2,59,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,15,3,1,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC

        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()
        t = time.mktime(datetime.datetime(2012,1,14,2,59,0).timetuple())
        assert t != t0
        assert sch.adjusted_now(t) < midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,14,3,0,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,15,2,59,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC
        t = time.mktime(datetime.datetime(2012,1,15,3,1,0).timetuple())
        assert sch.adjusted_now(t) >= midnight_UTC

    def test_1(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=[])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=[])[0]
        fact_data = {"f": "3", "b": "b"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=[])[0]
        fact_data = {"f": "4", "b": "b"}
        card_4 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=[])[0]
        card_4.next_rep -= 1000 * 24 * 60 * 60
        self.database().update_card(card_4)

        assert self.scheduler().next_card() == card_4
        self.scheduler().grade_answer(card_4, 0)
        assert card_4.active == True
        self.database().update_card(card_4)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 2)
        assert card.active == True
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 0)
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 1)
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards = [card]

        card = self.scheduler().next_card()
        assert card not in learned_cards
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards.append(card)

        assert self.scheduler().next_card() == None

        # Learn ahead.

        assert self.scheduler().next_card(learn_ahead=True) != None

    def test_1_bis(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=[])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=[])[0]
        fact_data = {"f": "3", "b": "b"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=[])[0]
        fact_data = {"f": "4", "b": "b"}
        card_4 = self.controller().create_new_cards(fact_data, card_type,
                     grade=2, tag_names=[])[0]
        card_4.next_rep -= 1000 * 24 * 60 * 60
        self.database().update_card(card_4)

        assert self.scheduler().next_card() == card_4
        self.scheduler().grade_answer(card_4, 1)

        assert card_4.active == True
        self.database().update_card(card_4)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 2)
        assert card.active == True
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 0)
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 1)
        self.database().update_card(card)

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards = [card]

        card = self.scheduler().next_card()
        assert card not in learned_cards
        self.scheduler().grade_answer(card, 2)
        self.database().update_card(card)
        learned_cards.append(card)

        assert self.scheduler().next_card() == None

        # Learn ahead.

        assert self.scheduler().next_card(learn_ahead=True) != None

    def test_2(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.config()["non_memorised_cards_in_hand"] = 0

        assert self.scheduler().next_card() is None

    def test_grade_0_limit(self):
        card_type = self.card_type_with_id("1")
        for i in range(10):
            fact_data = {"f": str(i), "b": "b"}
            self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.config()["non_memorised_cards_in_hand"] = 3
        cards = set()
        for i in range(10):
            card = self.scheduler().next_card()
            self.scheduler().grade_answer(card, 0)
            self.database().update_card(card)
            cards.add(card._id)
        assert len(cards) == 3

    def test_learn_ahead(self):
        card_type = self.card_type_with_id("1")
        for i in range(5):
            fact_data = {"f": str(i), "b": "b"}
            self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True
        for i in range(30):
            card = self.scheduler().next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)

        facts = self.scheduler()._fact_ids_learned_today()
        assert(len(facts)) == 5

    def test_learn_ahead_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        old_card = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True
        for i in range(3):
            card = self.scheduler().next_card(learn_ahead=True)
            self.scheduler().grade_answer(card, 5)
            self.database().update_card(card)
        fact_data = {"f": "2", "b": "b"}
        new_card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        assert self.scheduler().next_card() == new_card

        facts = self.scheduler()._fact_ids_learned_today()
        assert(len(facts)) == 1

    def test_4(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 0)
        card = self.scheduler().next_card()
        self.scheduler().grade_answer(card, 0)
        self.database().update_card(card)

        assert self.scheduler().next_card() != None

        facts = self.scheduler()._fact_ids_learned_today()
        assert(len(facts)) == 0

    def test_5(self):
        card_type = self.card_type_with_id("1")

        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]

        self.review_controller().show_new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(0)

        assert self.review_controller().card != None

    def test_6(self):
        card_1 = None
        self.review_controller().reset()
        for i in range(10):
            fact_data = {"f": "question" + str(i),
                         "b": "answer" + str(i)}
            if i % 2:
                card_type = self.card_type_with_id("1")
            else:
                card_type = self.card_type_with_id("2")
            card = self.controller().create_new_cards(fact_data, card_type,
                    grade=4, tag_names=["default" + str(i)])[0]
            card.next_rep = time.time() - 24 * 60 * 60
            card.last_rep = card.next_rep - i * 24 * 60 * 60
            self.database().update_card(card)
            if i == 0:
                card_1 = card
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(0)
        card_1_new = self.database().card(card_1._id, is_id_internal=True)
        assert card_1_new.grade == 0

    def test_learn_ahead_3(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(5)
        self.review_controller().learning_ahead = True
        for i in range(10):
            self.review_controller().show_new_question()
            assert self.review_controller().card is not None
            self.review_controller().grade_answer(2)

    def test_learn_ahead_4(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        self.review_controller().learning_ahead = True
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(0)
        assert self.review_controller().scheduled_count == 0

    def test_learn_sister_together(self):
        # Relax requirements if there are not enough cards.
        self.config()["memorise_sister_cards_on_same_day"] = False
        card_type = self.card_type_with_id("2")
        fact_data = {"f": "f", "b": "b"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().show_new_question()
        assert self.review_controller().card == card_1
        self.review_controller().grade_answer(5)
        cards = set()
        for i in range(30):
            self.review_controller().grade_answer(1)
            cards.add(self.review_controller().card._id)
        assert card_2._id in cards

    def test_order(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        card_1.next_rep = time.time() - 24 * 60 * 60
        card_1.last_rep = card_1.next_rep - 2 * 24 * 60 * 60
        self.database().update_card(card_1)
        fact_data = {"f": "2", "b": "b"}
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                     grade=5, tag_names=["default"])[0]
        card_2.next_rep = time.time() - 24 * 60 * 60
        card_2.last_rep = card_2.next_rep - 24 * 60 * 60
        self.database().update_card(card_2)

        # Shortest interval should go first.
        assert self.scheduler().next_card() == card_2

    def test_empty_tag(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "b"}
        card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=[])[0]
        self.review_controller().show_new_question()
        assert self.review_controller().card == card
        self.review_controller().grade_answer(2)
        self.review_controller().learning_ahead = True
        self.review_controller().show_new_question()
        assert self.review_controller().card == card

    def test_next_rep_to_interval_string(self):
        if sys.platform == "win32":
            return  # no time.tzset

        os.environ["TZ"] = "Europe/Brussels"
        time.tzset()

        sch = self.scheduler()
        now = datetime.datetime(2000, 9, 1, 12, 0)

        next_rep = now + datetime.timedelta(1)
        sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())))

        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "tomorrow"

        next_rep = now + datetime.timedelta(2)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "in 2 days"

        next_rep = now + datetime.timedelta(32)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "in 1 month"

        next_rep = now + datetime.timedelta(64)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "in 2 months"

        next_rep = now + datetime.timedelta(366)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "in 1.0 years"

        next_rep = now + datetime.timedelta(0)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "today"

        next_rep = now - datetime.timedelta(1)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "1 day overdue"

        next_rep = now - datetime.timedelta(2)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "2 days overdue"

        next_rep = now - datetime.timedelta(32)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "1 month overdue"

        next_rep = now - datetime.timedelta(64)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "2 months overdue"

        next_rep = now - datetime.timedelta(365)
        assert sch.next_rep_to_interval_string(\
            sch.midnight_UTC(calendar.timegm(next_rep.timetuple())),
            calendar.timegm(now.timetuple())) == \
            "1.0 years overdue"

    def test_next_rep_to_interval_string_2(self):
        if sys.platform == "win32":
            return  # no time.tzset
        os.environ["TZ"] = "Europe/Brussels"
        time.tzset()

        sch = self.scheduler()
        now = time.mktime(datetime.datetime(2000, 9, 1, 12, 0, 0).timetuple())
        now = sch.adjusted_now(now)

        next_rep = sch.midnight_UTC(now + DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "tomorrow"

        next_rep = sch.midnight_UTC(now + 2*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "in 2 days"

        next_rep = sch.midnight_UTC(now + 32*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "in 1 month"

        next_rep = sch.midnight_UTC(now + 64*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "in 2 months"

        next_rep = sch.midnight_UTC(now + 366*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "in 1.0 years"

        next_rep = sch.midnight_UTC(now)
        assert sch.next_rep_to_interval_string(next_rep, now) == "today"

        next_rep = sch.midnight_UTC(now - DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "1 day overdue"

        next_rep = sch.midnight_UTC(now - 2*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "2 days overdue"

        next_rep = sch.midnight_UTC(now - 32*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "1 month overdue"

        next_rep = sch.midnight_UTC(now - 64*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "2 months overdue"

        next_rep = sch.midnight_UTC(now - 366*DAY)
        assert sch.next_rep_to_interval_string(next_rep, now) == "1.0 years overdue"

    def test_last_rep_to_interval_string(self):
        if sys.platform == "win32":
            return  # no time.tzset
        os.environ["TZ"] = "Europe/Brussels"
        time.tzset()

        sch = self.scheduler()
        now = datetime.datetime(2000, 9, 1, 12, 0)

        last_rep = now + datetime.timedelta(0)
        sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()))

        last_rep = now + datetime.timedelta(0)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "today"

        last_rep = now - datetime.timedelta(1)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "yesterday"

        last_rep = now - datetime.timedelta(2)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "2 days ago"

        last_rep = now - datetime.timedelta(32)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "1 month ago"

        last_rep = now - datetime.timedelta(64)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "2 months ago"

        last_rep = now - datetime.timedelta(365)
        assert sch.last_rep_to_interval_string(\
            calendar.timegm(last_rep.timetuple()),
            calendar.timegm(now.timetuple())) == \
            "1.0 years ago"

    def test_last_rep_to_interval_string_2(self):
        if sys.platform == "win32":
            return  # no time.tzset
        sch = self.scheduler()
        os.environ["TZ"] = "Australia/Sydney"
        time.tzset()

        last_rep = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,5,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "today"

        last_rep = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,15,2,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "today"

        last_rep = time.mktime(datetime.datetime(2012,1,14,2,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "yesterday"

        last_rep = time.mktime(datetime.datetime(2012,1,13,5,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "yesterday"

    def test_last_rep_to_interval_string_3(self):
        if sys.platform == "win32":
            return  # no time.tzset
        sch = self.scheduler()
        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()

        last_rep = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,5,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "today"

        last_rep = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,15,2,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "today"

        last_rep = time.mktime(datetime.datetime(2012,1,14,2,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "yesterday"

        last_rep = time.mktime(datetime.datetime(2012,1,13,5,0,0).timetuple())
        now      = time.mktime(datetime.datetime(2012,1,14,4,0,0).timetuple())
        assert sch.last_rep_to_interval_string(last_rep, now) == "yesterday"


    def test_prefetch(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_0 = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]

        self.scheduler()._card_ids_in_queue = [card_0._id, card_1._id, card_1._id]
        assert self.scheduler().is_prefetch_allowed(card_to_grade=card_0) == False

    def test_prefetch_2(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_0 = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])[0]

        self.scheduler()._card_ids_in_queue = [card_0._id, card_1._id, card_0._id]
        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().show_answer()
        self.review_controller().grade_answer(2)
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)

    def test_prefetch_3(self):
        from mnemosyne.libmnemosyne.card_types.sentence import SentencePlugin
        for plugin in self.plugins():
            if isinstance(plugin, SentencePlugin):
                plugin.activate()
                break

        card_type = self.card_type_with_id("6")
        fact_data = {"f": "La [casa:house] es [grande:big] [a:b]"}
        cards = self.controller().create_new_cards(fact_data, card_type,
                                              grade=2, tag_names=["default"])
        self.review_controller().reset()
        self.review_controller().learning_ahead = True
        for i in range(4):
            self.review_controller().show_new_question()
            self.review_controller().show_answer()
            self.review_controller().grade_answer(2)
            assert self.review_controller().scheduled_count != -1

    def test_relearn(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_0 = self.controller().create_new_cards(fact_data, card_type,
                                              grade=5, tag_names=["default"])[0]
        card_0.next_rep = 0
        self.database().update_card(card_0)
        self.review_controller().reset()
        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().show_answer()
        assert self.review_controller().card is not None
        self.review_controller().grade_answer(0)
        assert self.review_controller().card is not None

    def test_stuck(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_0 = self.controller().create_new_cards(fact_data, card_type,
              grade=-1, tag_names=["default"])[0]

        self.review_controller().reset()
        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        self.review_controller().grade_answer(2)

        self.review_controller().learning_ahead = True
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().learning_ahead = False

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type = self.card_type_with_id("2")
        card_1, card_2 = self.controller().create_new_cards(fact_data, card_type,
              grade=-1, tag_names=["default"])

        while True:
            self.review_controller().show_answer()
            previous_card_id = self.review_controller().card._id
            if self.review_controller().card._id in [card_1._id, card_2._id]:
                if self.review_controller().card._id == card_1._id:
                    other_card = card_2
                else:
                    other_card = card_1
                self.review_controller().grade_answer(2)
                break
            self.review_controller().grade_answer(0)

        # Now we should get to see the other reverse card and not get stuck on the
        # failed card.

        # We also check whether we keep on alternating between the two
        # remaining cards.
        failed = True
        for i in range(100):
            self.review_controller().show_answer()
            assert self.review_controller().card._id != previous_card_id
            if self.review_controller().card._id == other_card._id:
                failed = False
            previous_card_id = self.review_controller().card._id
            self.review_controller().grade_answer(0)
        assert failed == False

    def test_filling(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card_0 = self.controller().create_new_cards(fact_data, card_type,
              grade=-1, tag_names=["default"])[0]

        unlearned = []
        for i in range(10):
            fact_data = {"f": str(i), "b": "b"}
            card = self.controller().create_new_cards(fact_data, card_type,
                     grade=-1, tag_names=["default"])[0]
            unlearned.append(card)
        self.config()["non_memorised_cards_in_hand"] = 4

        self.review_controller().reset()
        self.review_controller().show_new_question()
        self.review_controller().show_answer()
        self.review_controller().grade_answer(2)

        self.review_controller().learning_ahead = True
        self.review_controller().show_answer()
        self.review_controller().grade_answer(0)
        self.review_controller().learning_ahead = False

        showed_cards = set()
        for i in range(100):
            self.review_controller().show_answer()
            showed_cards.add(self.review_controller().card._id)
            self.review_controller().grade_answer(0)

        assert len(showed_cards) == 4

    def test_max_ret_reps_since_lapse(self):
        fact_data = {"f": "question1",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
              grade=2, tag_names=["default"])[0]
        card.ret_reps_since_lapse = 10
        card.next_rep = time.time()-10
        self.database().update_card(card)
        self.review_controller().reset()
        assert self.database().scheduled_count(time.time()) == 1

        self.config()["max_ret_reps_since_lapse"] = 5
        self.review_controller().reset()
        assert self.database().scheduled_count(time.time()) == 0


        
