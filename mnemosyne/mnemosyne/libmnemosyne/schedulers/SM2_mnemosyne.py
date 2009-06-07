#
# SM2_mnemosyne.py <Peter.Bienstman@UGent.be>
#

import time
import random
import calendar
import datetime

from mnemosyne.libmnemosyne.scheduler import Scheduler
from mnemosyne.libmnemosyne.stopwatch import stopwatch

DAY = 24 * 60 * 60 # Seconds in a day.


class SM2Mnemosyne(Scheduler):

    """Scheduler based on http://www.supermemo.com/english/ol/sm2.htm.
    Note that all intervals are in seconds, since time is stored as
    integer POSIX timestamps.

    Since the scheduling granularity is days, all cards due on the same time
    should become due at the same time. In order to keep the SQL query
    efficient, we do this by setting 'next_rep' the same for all cards that
    are due on the same day.
    
    In order to allow for the fact that the time zone and 'day_starts_at' can
    change after scheduling a card, we store 'next_rep' as midnight UTC, and
    bring local time and 'day_starts_at' only into play when querying the
    database.

    """
    
    name = "SM2 Mnemosyne"

    def midnight_UTC(self, timestamp):        
        date_only = datetime.date.fromtimestamp(timestamp)
        return int(calendar.timegm(date_only.timetuple()))
    
    def adjusted_now(self):

        """Adjust now such that the cross-over point of h:00 local time
        (with h being 'day_starts_at') to midnight UTC.

        """

        now = time.time()
        now -= self.config()["day_starts_at"] * 60 * 60            
        if time.daylight:
            now -= time.altzone
        else:
            now -= time.timezone
        return int(now)

    def true_scheduled_interval(self, card):

        """Since 'next_rep' is always midnight UTC for retention reps, we need
        to take timezone and 'day_starts_at' into account to calculate the true
        scheduled interval when we are doing the actual repetition.

        """

        interval = card.next_rep - card.last_rep
        if card.grade < 2:
            return interval
        interval += self.config()["day_starts_at"] * 60 * 60            
        if time.daylight:
            interval += time.altzone
        else:
            interval += time.timezone
        return int(interval)       
    
    def reset(self):
        self.queue = []
        self.facts = []
        self.last_card = None # To avoid showing the same card twice in a row.
        self.stage = 1 # Allow skipping unnecessary queries.
                
    def set_initial_grade(self, card, grade):

        """Note that even if the initial grading happens when adding a card, it
        is seen as a repetition.

        """

        card.grade = grade
        card.easiness = self.database().average_easiness()
        card.acq_reps = 1
        card.acq_reps_since_lapse = 1
        card.last_rep = time.time()
        new_interval = self.calculate_initial_interval(grade)
        new_interval += self.calculate_interval_noise(new_interval)
        if grade >= 2:
            card.next_rep = self.midnight_UTC(card.last_rep + new_interval)
        else:
            card.next_rep = time.time()            
        self.log().repetition(card, scheduled_interval=0, actual_interval=0,
                              new_interval=new_interval)

    def calculate_initial_interval(self, grade):
        
        """The first repetition is treated specially, and gives longer
        intervals, to allow for the fact that the user may have seen this
        card before.

        """
        
        return (0, 0, 1*DAY, 3*DAY, 4*DAY, 5*DAY) [grade]

    def calculate_interval_noise(self, interval):
        if interval == 0:
            noise = 0
        elif interval <= DAY:
            noise = random.choice([0, DAY])
        elif interval <= 10 * DAY:
            noise = random.choice([-DAY, 0, DAY])
        elif interval <= 60 * DAY:
            noise = random.uniform(-3 * DAY, 3 * DAY)
        else:
            noise = random.uniform(-0.05 * interval, 0.05 * interval)
        return noise

    def rebuild_queue(self, learn_ahead=False):
        self.queue = []
        self.facts = []
        db = self.database()
        if not db.is_loaded() or not db.active_count():
            return
        
        # Stage 1
        #
        # Do the cards that are scheduled for today (or are overdue), but
        # first do those that have the shortest interval, as being a day
        # late on an interval of 2 could be much worse than being a day late
        # on an interval of 50.
        # Fetch maximum 50 cards at the same time, as a trade-off between
        # memory usage and redoing the query.
        if self.stage == 1:
            if self.config()["randomise_scheduled_cards"] == True:
                sort_key = "random"
            else:
                sort_key = "interval"
            for _card_id, _fact_id in db.cards_due_for_ret_rep(\
                    self.adjusted_now(), sort_key=sort_key, limit=50):
                self.queue.append(_card_id)
                self.facts.append(_fact_id)
            if len(self.queue):
                return
            self.stage = 2

        # Stage 2
        #
        # Now rememorise the cards that we got wrong during the last stage.
        # Concentrate on only a limited number of grade 0 cards, in order to
        # avoid too long intervals between repetitions.
        limit = self.config()["grade_0_items_at_once"]
        grade_0_in_queue = 0
        if self.stage == 2:
            if limit:
                for _card_id, _fact_id in \
                        db.cards_due_for_final_review(grade=0):
                    if _fact_id not in self.facts:
                        if grade_0_in_queue < limit:
                            self.queue.append(_card_id)
                            self.queue.append(_card_id)
                            self.facts.append(_fact_id)
                            grade_0_in_queue += 1
                        if grade_0_in_queue == limit:
                            break       
            for _card_id, _fact_id in db.cards_due_for_final_review(grade=1):
                if _fact_id not in self.facts:
                    self.queue.append(_card_id)
                    self.facts.append(_fact_id)
            random.shuffle(self.queue)
            # Only stop when we reach the grade 0 limit. Otherwise, keep
            # going to add some extra cards to get more spread.
            if limit and grade_0_in_queue == limit:
                return
            if len(self.queue) == 0:
                self.stage = 3

        # Stage 3
        #
        # Now do the cards which have never been committed to long-term
        # memory, but which we have seen before.
        if self.stage == 3:
            if limit:
                for _card_id, _fact_id in db.cards_new_memorising(grade=0):
                    if _fact_id not in self.facts:
                        if grade_0_in_queue < limit:
                            self.queue.append(_card_id)
                            self.queue.append(_card_id)
                            self.facts.append(_fact_id)
                            grade_0_in_queue += 1
                        if grade_0_in_queue == limit:
                            break       
            for _card_id, _fact_id in db.cards_new_memorising(grade=1):
                if _fact_id not in self.facts:
                    self.queue.append(_card_id)
                    self.facts.append(_fact_id)
            random.shuffle(self.queue)
            # Only stop when we reach the grade 0 limit. Otherwise, keep
            # going to add some extra cards to get more spread.
            if limit and grade_0_in_queue == limit:
                return
            if len(self.queue) == 0:
                self.stage = 4

        # Stage 4
        #
        # Now add some unseen cards.
        if self.stage <= 4:
            if self.config()["randomise_new_cards"]:
                sort_key = "random"
            else:
                sort_key = ""
            for _card_id, _fact_id in db.cards_unseen(grade=1, sort_key=sort_key,
                                                      limit=50):
                if _fact_id not in self.facts:
                    self.queue.append(_card_id)
                    self.facts.append(_fact_id)        
            if limit:
                for _card_id, _fact_id in db.cards_unseen(grade=0, sort_key=sort_key,
                                                          limit=limit):
                    if _fact_id not in self.facts:
                        self.queue.append(_card_id)
                        self.facts.append(_fact_id)
                        grade_0_in_queue += 1
                        if grade_0_in_queue == limit:
                            self.stage = 2
                            return
            # Ungraded cards (with grade -1) are treated as grade 0 cards here in
            # terms of limiting the queue size.
            if limit:
                for _card_id, _fact_id in db.cards_unseen(grade=-1, sort_key=sort_key,
                                                          limit=limit):
                    if _fact_id not in self.facts:
                        self.queue.append(_card_id)
                        self.facts.append(_fact_id)
                        grade_0_in_queue += 1
                        if grade_0_in_queue == limit:
                            self.stage = 2
                            return
            if len(self.queue) == 0:
                self.stage = 5
            
        # Stage 5
        #
        # If we get to here, there are no more scheduled cards or new cards
        # to learn. The user can signal that he wants to learn ahead by
        # calling rebuild_queue with 'learn_ahead' set to True.
        # Don't shuffle this queue, as it's more useful to review the
        # earliest scheduled cards first. We only put 50 cards at the same
        # time into the queue, in order to save memory.
        if learn_ahead == False:
            self.stage = 3
            return
        for _card_id, _fact_id in db.cards_learn_ahead(self.adjusted_now(),
                sort_key="next_rep", limit=50):
            self.queue.append(_card_id)
        # Relearn cards which we got wrong during learn ahead.
        self.stage = 2

    def in_queue(self, card):
        return card._id in self.queue
    
    def remove_from_queue(self, card):
        try:
            self.queue.remove(card._id)
            self.queue.remove(card._id)
        except:
            pass
    
    def get_next_card(self, learn_ahead=False):
        # Populate queue if it is empty.
        if len(self.queue) == 0:
            self.rebuild_queue(learn_ahead)
            if len(self.queue) == 0:
                return None
        # Pick the first card and remove it from the queue. Make sure we don't
        # show the same card twice in succession, unless the queue becomes too
        # small and we risk running out of cards.
        _card_id = self.queue.pop(0)
        if self.last_card:
            while len(self.queue) >= 3 and self.last_card == _card_id:
                _card_id = self.queue.pop(0)
        self.last_card = _card_id
        return self.database().get_card(_card_id)

    def allow_prefetch(self):

        """Can we display a new card before having processed the grading of
        the previous one?

        """
                
        # Make sure there are enough cards left to find one which is not a
        # duplicate.
        return len(self.queue) >= 3

    def grade_answer(self, card, new_grade, dry_run=False):
        # When doing a dry run, make a copy to operate on. This leaves the
        # original in the GUI intact.
        if dry_run:
            import copy
            card = copy.copy(card)
        scheduled_interval = self.true_scheduled_interval(card)
        actual_interval = stopwatch.start_time - card.last_rep
        if card.acq_reps == 0 and card.ret_reps == 0:
            # The card has not yet been given its initial grade, because it
            # was imported or created during card type conversion.
            card.easiness = self.database().average_easiness()
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
            new_interval = self.calculate_initial_interval(new_grade)
            # Make sure the second copy of a grade 0 card doesn't show
            # up again.
            if not dry_run and card.grade == 0 and new_grade in [2, 3, 4, 5]:
                if card._id in self.queue:
                    self.queue.remove(card._id)    
        elif card.grade in [0, 1] and new_grade in [0, 1]:
            # In the acquisition phase and staying there.
            card.acq_reps += 1
            card.acq_reps_since_lapse += 1
            new_interval = 0
        elif card.grade in [0, 1] and new_grade in [2, 3, 4, 5]:
             # In the acquisition phase and moving to the retention phase.
             card.acq_reps += 1
             card.acq_reps_since_lapse += 1
             new_interval = DAY
             # Make sure the second copy of a grade 0 card doesn't show
             # up again.
             if not dry_run and card.grade == 0:
                if card._id in self.queue:
                    self.queue.remove(card._id)
        elif card.grade in [2, 3, 4, 5] and new_grade in [0, 1]:
             # In the retention phase and dropping back to the
             # acquisition phase.
             card.ret_reps += 1
             card.lapses += 1
             card.acq_reps_since_lapse = 0
             card.ret_reps_since_lapse = 0
             new_interval = 0
        elif card.grade in [2, 3, 4, 5] and new_grade in [2, 3, 4, 5]:
            # In the retention phase and staying there.
            card.ret_reps += 1
            card.ret_reps_since_lapse += 1
            if actual_interval >= scheduled_interval:
                if new_grade == 2:
                    card.easiness -= 0.16
                if new_grade == 3:
                    card.easiness -= 0.14
                if new_grade == 5:
                    card.easiness += 0.10
                if card.easiness < 1.3:
                    card.easiness = 1.3
            if card.ret_reps_since_lapse == 1:
                new_interval = 6 * DAY
            else:
                if new_grade == 2 or new_grade == 3:
                    if actual_interval <= scheduled_interval:
                        new_interval = actual_interval * card.easiness
                    else:
                        new_interval = scheduled_interval
                if new_grade == 4:
                    new_interval = actual_interval * card.easiness
                if new_grade == 5:
                    if actual_interval < scheduled_interval:
                        new_interval = scheduled_interval # Avoid spacing.
                    else:
                        new_interval = actual_interval * card.easiness
        new_interval = int(new_interval)
        # When doing a dry run, stop here and return the scheduled interval.
        if dry_run:
            return new_interval

        # Add some randomness to interval.
        new_interval += self.calculate_interval_noise(new_interval)
        # Update card properties.
        card.grade = new_grade
        card.last_rep = time.time()
        if new_grade >= 2:
            card.next_rep = self.midnight_UTC(card.last_rep + new_interval)
            # Don't schedule related cards on the same day. Keep normalising,
            # as a day is not always exactly DAY seconds when there are leap
            # seconds. 
            while self.database().count_related_cards_with_next_rep\
                  (card, card.next_rep):
                card.next_rep = self.midnight_UTC(card.next_rep + DAY)
            # Round new interval to nearest cross-over point (only used in
            # logging here).
            new_interval = self.true_scheduled_interval(card)
        else:
            card.next_rep = time.time()
            new_interval = 0
        card.unseen = False
        # Run post review hooks.
        card.fact.card_type.after_review(card)
        # Create log entry.
        self.log().repetition(card, scheduled_interval, actual_interval,
                              new_interval)
        return new_interval

    def non_memorised_count(self):
        return self.database().non_memorised_count()

    def scheduled_count(self):
        return self.database().scheduled_count(self.adjusted_now())

    def active_count(self):
        return self.database().active_count()

