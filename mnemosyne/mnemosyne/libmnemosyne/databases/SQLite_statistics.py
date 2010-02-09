#
# SQLite_statistics.py <Peter.Bienstman@UGent.be>
#

import time
import datetime

from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.utils import numeric_string_cmp

HOUR = 60 * 60 # Seconds in an hour. 
DAY = 24 * HOUR # Seconds in a day.


class SQLiteStatistics(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """

    def get_tags__id_and_name(self):
        result = [(cursor[0], cursor[1]) for cursor in self.con.execute(\
            "select _id, name from tags")]
        result.sort(key=lambda x: x[1], cmp=numeric_string_cmp)
        return result
        
    def easinesses(self):
        return [cursor[0] for cursor in self.con.execute(\
            "select easiness from cards where active=1 and grade>=0")]

    def easinesses_for__tag_id(self, _tag_id):    
        return [cursor[0] for cursor in self.con.execute(\
            """select cards.easiness from cards, tags_for_card where
            tags_for_card._card_id=cards._id and cards.active=1 and
            cards.grade>=0 and tags_for_card._tag_id=?""", (_tag_id, ))]

    def card_count_for_grade(self, grade):
        return self.con.execute(\
            "select count() from cards where grade=? and active=1",
            (grade, )).fetchone()[0]
 
    def card_count_for_grade_and__tag_id(self, grade, _tag_id):
        return self.con.execute(\
             """select count() from cards, tags_for_card where
             tags_for_card._card_id=cards._id and cards.active=1
             and tags_for_card._tag_id=? and grade=?""",
             (_tag_id, grade)).fetchone()[0]

    def total_card_count_for_grade(self, grade):
        return self.con.execute("select count() from cards where grade=?",
            (grade, )).fetchone()[0]
    
    def total_card_count_for__tag_id(self, _tag_id):
        return self.con.execute(\
             """select count() from cards, tags_for_card where
             tags_for_card._card_id=cards._id and tags_for_card._tag_id=?""",
             (_tag_id, )).fetchone()[0]
    
    def total_card_count_for_grade_and__tag_id(self, grade, _tag_id):
        return self.con.execute(\
            """select count() from cards, tags_for_card where
              tags_for_card._card_id=cards._id and tags_for_card._tag_id=?
              and grade=?""", (_tag_id, grade)).fetchone()[0]
 
    def future_card_count_scheduled_between(self, start, stop):
        return self.con.execute(\
            """select count() from cards where active=1 and grade>=2
            and ?<next_rep and next_rep<=?""",
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
        print start_of_day
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
