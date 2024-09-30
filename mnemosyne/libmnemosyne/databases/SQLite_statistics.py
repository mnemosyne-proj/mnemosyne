#
# SQLite_statistics.py <Peter.Bienstman@gmail.com>
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
            where active=1 and grade>=2 and ?>=next_rep
            and ret_reps_since_lapse<=?""", (timestamp,
            self.config()["max_ret_reps_since_lapse"])).fetchone()[0]
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

        # TODO: profile to determine the most efficient version

        #return self.con.execute("""select count() from cards where active=1
        #    and grade>=2 and ?<=next_rep and next_rep<? and _id<>? and _id in
        #    (select _id from cards where _fact_id=?)""",
        #    (start, stop, card._id, card.fact._id)).fetchone()[0]

        #return self.con.execute("""select count() from cards where _id in
        #    (select _id from cards where _fact_id=?) and active=1
        #    and grade>=2 and ?<=next_rep and next_rep<? and _id<>?""",
        #    (card.fact._id, start, stop, card._id)).fetchone()[0]

        #_card_ids = [cursor[0] for cursor in self.con.execute(\
        #    "select _id from cards where _fact_id=?", (card.fact._id, ))]
        #query = "select count() from cards where _id in ("
        #for _card_id in _card_ids:
        #    query += str(_card_id) + ","
        #query = query[:-1] + """) and active=1 and grade>=2 and
        #    ?<=next_rep and next_rep<? and _id<>?"""
        #return self.con.execute(query, (start, stop, card._id)).fetchone()[0]

        _card_ids = [cursor[0] for cursor in self.con.execute(\
            "select _id from cards where _fact_id=?", (card.fact._id, ))]
        if len(_card_ids) == 1: # No sister cards
            return 0
        query = "select active, grade, next_rep from cards where _id in ("
        for _card_id in _card_ids:
            if _card_id != card._id:
                query += str(_card_id) + ","
        query = query[:-1] + """)"""
        count = 0
        for cursor in self.con.execute(query):
            if cursor[0] == True and cursor[1] >= 2 \
                and start <= cursor[2] < stop:
                count += 1
        return count

    def card_count_scheduled_between(self, start, stop):
        return self.con.execute(\
            """select count() from cards where grade>=2 and ?<=next_rep and
            next_rep<? and ret_reps_since_lapse<=? and active='1'""",
            (start, stop,
             self.config()["max_ret_reps_since_lapse"])).fetchone()[0]

    def start_of_day_n_days_ago(self, n):
        timestamp = time.time() - n * DAY \
                    - self.config()["day_starts_at"] * HOUR
        # Roll this back to the midnight before.
        date_only = datetime.date.fromtimestamp(timestamp) # Local date.
        start_of_day = int(time.mktime(date_only.timetuple()))
        # Bring back to 0:h with h="day_starts_at"
        start_of_day += self.config()["day_starts_at"] * HOUR
        return start_of_day

    def card_count_scheduled_n_days_ago(self, n):
        start_of_day = self.start_of_day_n_days_ago(n)
        actual_counts_for_machine = {}
        projected_counts_for_machine = {}
        # For each machine id, get the number of cards that were scheduled
        # that day. Make a distinction between the actual schedule and the
        # scheduled that was projected in the future during database load
        # events. For each machine, we take the largest number in the logs,
        # i.e. those at the start of the day.
        for cursor in self.con.execute("""select acq_reps, object_id from log
            where ?<=timestamp and timestamp<? and (event_type=? or
            event_type=?)""", (start_of_day, start_of_day + DAY,
            EventTypes.LOADED_DATABASE, EventTypes.SAVED_DATABASE)):
            count = cursor[0]
            machine = cursor[1]
            # Future projected schedule. Check if machine exists to deal with
            # Mnemosyne versions before 201203.
            if machine and machine.endswith(".fut"):
                if not machine in projected_counts_for_machine or \
                    (projected_counts_for_machine[machine] < count):
                    projected_counts_for_machine[machine] = count
            # Actual schedule.
            else:
                if not machine in actual_counts_for_machine or \
                    (actual_counts_for_machine[machine] < count):
                    actual_counts_for_machine[machine] = count
        # In case several machines report a different scheduded count, take
        # the minimum, as we assume that the larger number corresponds to
        # another machine which was kept running and therefore accumulated a
        # backlog, while the actual reviews happened on another machine.
        if len(actual_counts_for_machine) != 0:
            return min(actual_counts_for_machine.values())
        # In case there is no actual data, use the projected data, taking the
        # maximum over all possible machines.
        elif len(projected_counts_for_machine) != 0:
            return max(projected_counts_for_machine.values())
        # If there is no data, return 0 for unknown.
        else:
            return 0
        # Note that the algorithm above is still an approximation, e.g. there
        # is no way it can know about different cards sets that are active
        # during the day.
        # It can also go wrong after resolution of a sync conflict when all the
        # reviews are done for the day.

    def card_count_added_n_days_ago(self, n):
        start_of_day = self.start_of_day_n_days_ago(n)
        return self.con.execute(\
            """select count() from log where ?<=timestamp and timestamp<?
            and event_type=?""",
            (start_of_day, start_of_day + DAY, EventTypes.ADDED_CARD)).\
            fetchone()[0]

    def card_count_learned_n_days_ago(self, n):
        start_of_day = self.start_of_day_n_days_ago(n)
        return self.con.execute(\
            """select count() from log where ?<=timestamp and timestamp<?
            and event_type=? and grade>=2 and ret_reps==0""",
            (start_of_day, start_of_day + DAY, EventTypes.REPETITION)).\
            fetchone()[0]

    def retention_score_n_days_ago(self, n):
        start_of_day = self.start_of_day_n_days_ago(n)
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
