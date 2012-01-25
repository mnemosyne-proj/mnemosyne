#
# SQLite_statistics.py <Peter.Bienstman@UGent.be>
#

import time
import datetime

from openSM2sync.log_entry import EventTypes

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


class SQLiteStatistics(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """

    def tag_count(self):
        return self.con.execute("select count() from tags").fetchone()[0]

    def fact_count(self):
        return self.con.execute("select count() from facts").fetchone()[0]

    def card_count(self):
        return self.con.execute("""select count() from cards""").fetchone()[0]

    def non_memorised_count(self):
        return self.con.execute("""select count() from cards
            where active=1 and grade<2""").fetchone()[0]

    def scheduled_count(self, timestamp):
        count = self.con.execute("""select count() from cards
            where active=1 and grade>=2 and ?>=next_rep""",
            (timestamp, )).fetchone()[0]
        return count

    def active_count(self):
        return self.con.execute("""select count() from cards
            where active=1""").fetchone()[0]

    def easinesses(self, active_only):
        query = "select easiness from cards where grade>=0"
        if active_only:
            query += " and active=1"
        return [cursor[0] for cursor in self.con.execute(query)]

    def easinesses_for_tag(self, tag, active_only):
        query = """select cards.easiness from cards, tags_for_card where
            tags_for_card._card_id=cards._id and cards.grade>=0 and
            tags_for_card._tag_id=?"""
        if active_only:
            query += " and cards.active=1"
        return [cursor[0] for cursor in self.con.execute(query,
            (tag._id, ))]

    def card_count_for_fact_view(self, fact_view, active_only):
        query = "select count() from cards where fact_view_id=?"
        if active_only:
            query += " and active=1"
        return self.con.execute(query, (fact_view.id, )).fetchone()[0]

    def card_count_for_grade(self, grade, active_only):
        query = "select count() from cards where grade=?"
        if active_only:
            query += " and active=1"
        return self.con.execute(query, (grade, )).fetchone()[0]

    def card_count_for_tags(self, tags, active_only):

        """ Determine the number of cards in a set of tags. Note that a card
        could have one or more of these tags.

        """

        if len(tags) == 0:
            return 0
        if active_only == True:
            raise NotImplementedError
        query = "select count(distinct _card_id) from tags_for_card where "
        args = []
        # Since tag typically contains 1 element, a query with 'or' is faster
        # than one with 'in ()'.
        for tag in tags:
            query += "_tag_id=? or "
            args.append(tag._id)
        query = query.rsplit("or ", 1)[0]
        return self.con.execute(query, args).fetchone()[0]

    def card_count_for_grade_and_tag(self, grade, tag, active_only):
        query = """select count() from cards, tags_for_card where
            tags_for_card._card_id=cards._id and tags_for_card._tag_id=?
            and grade=?"""
        if active_only:
            query += " and cards.active=1"
        return self.con.execute(query, (tag._id, grade)).fetchone()[0]

    def sister_card_count_scheduled_between(self, card, start, stop):

        """Return how many sister cards with grade >= 2 are scheduled at
        between 'start' (included) and 'stop' (excluded).

        """

        return self.con.execute("""select count() from cards where active=1
            and grade>=2 and ?<=next_rep and next_rep<? and _id<>? and _id in
            (select _id from cards where _fact_id=?)""",
            (start, stop, card._id, card.fact._id)).fetchone()[0]

    def card_count_scheduled_between(self, start, stop):
        return self.con.execute(\
            """select count() from cards where active=1 and grade>=2
            and ?<=next_rep and next_rep<?""",
            (start, stop)).fetchone()[0]

    def _start_of_day_n_days_ago(self, n):
        timestamp = time.time() - n * DAY \
                    - self.config()["day_starts_at"] * HOUR
        date_only = datetime.date.fromtimestamp(timestamp)
        start_of_day = int(time.mktime(date_only.timetuple()))
        start_of_day += self.config()["day_starts_at"] * HOUR
        return start_of_day

    def card_count_scheduled_n_days_ago(self, n):
        start_of_day = self._start_of_day_n_days_ago(n)
        result = self.con.execute(\
            """select acq_reps from log where ?<=timestamp and timestamp<?
            and (event_type=? or event_type=?) order by acq_reps desc
            limit 1""", (start_of_day, start_of_day + DAY,
            EventTypes.LOADED_DATABASE, EventTypes.SAVED_DATABASE)).fetchone()
        if result:
            return result[0]
        else:
            return 0 # Unknown.

    def card_count_added_n_days_ago(self, n):
        start_of_day = self._start_of_day_n_days_ago(n)
        return self.con.execute(\
            """select count() from log where ?<=timestamp and timestamp<?
            and event_type=?""",
            (start_of_day, start_of_day + DAY, EventTypes.ADDED_CARD)).\
            fetchone()[0]

    def retention_score_n_days_ago(self, n):
        start_of_day = self._start_of_day_n_days_ago(n)
        scheduled_cards_seen = self.con.execute(\
            """select count() from log where ?<=timestamp and timestamp<?
            and event_type=? and scheduled_interval!=0""",
            (start_of_day, start_of_day + DAY, EventTypes.REPETITION)).\
            fetchone()[0]
        if scheduled_cards_seen == 0:
            return 0
        scheduled_cards_correct = self.con.execute(\
            """select count() from log where ?<=timestamp and timestamp<?
            and event_type=? and scheduled_interval!=0 and grade>=2""",
            (start_of_day, start_of_day + DAY, EventTypes.REPETITION)).\
            fetchone()[0]
        return 100.0 * scheduled_cards_correct / scheduled_cards_seen

    def average_thinking_time(self, card):
        result = self.con.execute(\
            """select avg(thinking_time) from log where object_id=?
            and event_type=?""",
            (card.id, EventTypes.REPETITION)).fetchone()[0]
        if result:
            return result
        else:
            return 0

    def total_thinking_time(self, card):
        result = self.con.execute(\
            """select sum(thinking_time) from log where object_id=?
            and event_type=?""",
            (card.id, EventTypes.REPETITION)).fetchone()[0]
        if result:
            return result
        else:
            return 0
