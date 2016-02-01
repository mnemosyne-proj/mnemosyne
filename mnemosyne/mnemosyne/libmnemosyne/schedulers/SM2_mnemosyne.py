#
# SM2_mnemosyne.py <Peter.Bienstman@UGent.be>
#

import time
import random
import calendar
import datetime

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.scheduler import Scheduler

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


class SM2Mnemosyne(Scheduler):

    """Scheduler based on http://www.supermemo.com/english/ol/sm2.htm.
    Note that all intervals are in seconds, since time is stored as
    integer POSIX timestamps.

    Since the scheduling granularity is days, all cards due on the same time
    should become due at the same time. In order to keep the SQL query
    efficient, we do this by setting 'next_rep' the same for all cards that
    are due on the same day.

    In order to allow for the fact that the timezone and 'day_starts_at' can
    change after scheduling a card, we store 'next_rep' as midnight UTC, and
    bring local time and 'day_starts_at' only into play when querying the
    database.

    """

    name = "SM2 Mnemosyne"

    def midnight_UTC(self, timestamp):

        """Round a timestamp to a value with resolution of a day, storing it
        in a timezone independent way, as a POSIX timestamp corresponding to
        midnight UTC on that date.

        E.g. if the scheduler sets 'next_rep' to 2012/1/1 12:14 local time,
        this function will return the timestamp corresponding to
        2012/1/1 00;00 UTC.

        Important: the timestamp needs to have the meaning of local time,
        not e.g. UTC, so calling midnight_UTC twice will give unexpected
        results.

        """

        # Create a time tuple containing the local date only, i.e. throwing
        # away hours, minutes, etc.
        date_only = datetime.date.fromtimestamp(timestamp).timetuple()
        # Now we reinterpret this same time tuple as being UTC and convert it
        # to a POSIX timestamp. (Note that timetuples are 'naive', i.e. they
        # themselves do not contain timezone information.)
        return int(calendar.timegm(date_only))

    def adjusted_now(self, now=None):

        """Timezone information and 'day_starts_at' will only become relevant
        when the queue is built, not at schedule time, to allow for
        moving to a different timezone after a card has been scheduled.
        Cards are due when 'adjusted_now >= next_rep', and this function
        makes sure that happens at h:00 local time (with h being
        'day_starts_at').

        """

        if now == None:
            now = time.time()
        # The larger 'day_starts_at', the later the card should become due,
        # i.e. larger than 'next_card', so the more 'now' should be decreased.
        now -= self.config()["day_starts_at"] * HOUR
        # 'altzone' or 'timezone' contains the offset in seconds west of UTC.
        # This number is positive for the US, where a card should become
        # due later than in Europe, so 'now' should be decreased by this
        # offset.
        # As for when to use 'altzone' instead of 'timezone' if daylight
        # savings time is active, this is a matter of big confusion
        # among the Python developers themselves:
        # http://bugs.python.org/issue7229
        if time.localtime(now).tm_isdst and time.daylight:
            now -= time.altzone
        else:
            now -= time.timezone
        return int(now)

    def true_scheduled_interval(self, card):

        """Since 'next_rep' is always midnight UTC for retention reps, we need
        to take timezone and 'day_starts_at' into account to calculate the
        true scheduled interval when we are doing the actual repetition.
        This basically undoes the operations from 'adjusted_now'.
        Note that during the transition between different timezones, this is
        not well-defined, but the influence on the scheduler will be minor
        anyhow.

        """

        interval = card.next_rep - card.last_rep
        if card.grade < 2:
            if interval != 0:
                self.main_widget().show_error("Internal error: interval not zero.")
            #assert interval == 0
            return interval
        interval += self.config()["day_starts_at"] * HOUR
        if time.localtime(time.time()).tm_isdst and time.daylight:
            interval += time.altzone
        else:
            interval += time.timezone
        return int(interval)

    def reset(self):

        """'_card_ids_in_queue' contains the _ids of the cards making up the
        queue.

        The corresponding fact._ids are also stored in '_fact_ids_in_queue',
        which is needed to make sure that no sister cards can be together in
        the queue at any time.

        '_fact_ids_memorised' has a different function and persists over the
        different stages invocations of 'rebuild_queue'. It can be used to
        control whether or not memorising a card will prevent a sister card
        from being pulled out of the 'unseen' pile, even after the queue has
        been rebuilt.

        '_card_id_last' is stored to avoid showing the same card twice in a
        row.

        'stage' stores the stage of the queue building, and is used to skip
        over unnecessary queries.

        """

        self._card_ids_in_queue = []
        self._fact_ids_in_queue = []
        self._fact_ids_memorised = []
        self._card_id_last = None
        self.stage = 1
        self.warned_about_too_many_cards = False     

    def set_initial_grade(self, cards, grade):

        """Sets the initial grades for a set of sister cards, making sure
        their next repetitions do no fall on the same day.

        Note that even if the initial grading happens when adding a card, it
        is seen as a repetition.

        """

        new_interval = self.calculate_initial_interval(grade)
        new_interval += self.calculate_interval_noise(new_interval)
        last_rep = int(time.time())
        next_rep = self.midnight_UTC(last_rep + new_interval)
        for card in cards:
            card.grade = grade
            card.easiness = 2.5
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
            card.last_rep = last_rep
            card.next_rep = next_rep
            next_rep += DAY
            self.log().repetition(card, scheduled_interval=0,
                actual_interval=0, thinking_time=0)

    def calculate_initial_interval(self, grade):

        """The first repetition is treated specially, and gives longer
        intervals, to allow for the fact that the user may have seen this
        card before.

        """

        return (0, 0, 1*DAY, 3*DAY, 4*DAY, 7*DAY) [grade]

    def calculate_interval_noise(self, interval):
        if interval == 0:
            noise = 0
        elif interval <= 10 * DAY:
            noise = random.choice([0, DAY])
        elif interval <= 60 * DAY:
            noise = random.uniform(-3 * DAY, 3 * DAY)
        else:
            noise = random.uniform(-0.05 * interval, 0.05 * interval)
        return int(noise)

    def avoid_sister_cards(self, card):

        """Change card.next_rep to make sure that the card is not scheduled
        on the same day as a sister card.

        Factored out here to allow this to be used by e.g. MnemoGogo.

        """

        while self.database().sister_card_count_scheduled_between\
            (card, card.next_rep, card.next_rep + DAY):
            card.next_rep += DAY

    def rebuild_queue(self, learn_ahead=False):
        db = self.database()
        if not db.is_loaded() or not db.active_count():
            return
        self._card_ids_in_queue = []
        self._fact_ids_in_queue = []

        # Stage 1
        #
        # Do the cards that are scheduled for today (or are overdue), but
        # first do those that have the shortest interval, as being a day
        # late on an interval of 2 could be much worse than being a day late
        # on an interval of 50.
        # Fetch maximum 50 cards at the same time, as a trade-off between
        # memory usage and redoing the query.
        if self.stage == 1:
            if self.config()["shown_backlog_help"] == False:
                if db.scheduled_count(self.adjusted_now() - DAY) != 0:
                    self.main_widget().show_information(_("You appear to have missed some reviews. Don't worry too much about this backlog, and do as many cards as you feel comfortable with to catch up each day. Mnemosyne will automatically reschedule your cards such that the most urgent ones are shown first."))
                    self.config()["shown_backlog_help"] = True
            if self.config()["randomise_scheduled_cards"] == True:
                sort_key = "random"
            else:
                sort_key = "interval"
            for _card_id, _fact_id in db.cards_due_for_ret_rep(\
                    self.adjusted_now(), sort_key=sort_key, limit=50):
                self._card_ids_in_queue.append(_card_id)
                self._fact_ids_in_queue.append(_fact_id)
            if len(self._card_ids_in_queue):
                return
            self.stage = 2

        # Stage 2
        #
        # Now rememorise the cards that we got wrong during the last stage.
        # Concentrate on only a limited number of non memorised cards, in
        # order to avoid too long intervals between repetitions.
        limit = self.config()["non_memorised_cards_in_hand"]
        non_memorised_in_queue = 0
        if self.stage == 2:
            for _card_id, _fact_id in db.cards_to_relearn(grade=1,
                sort_key="-interval"):
                if _fact_id not in self._fact_ids_in_queue:
                    if non_memorised_in_queue < limit:
                        self._card_ids_in_queue.append(_card_id)
                        self._fact_ids_in_queue.append(_fact_id)
                        non_memorised_in_queue += 1
                    if non_memorised_in_queue == limit:
                        break
            for _card_id, _fact_id in db.cards_to_relearn(grade=0,
                sort_key="-interval"):
                if _fact_id not in self._fact_ids_in_queue:
                    if non_memorised_in_queue < limit:
                        self._card_ids_in_queue.append(_card_id)
                        self._card_ids_in_queue.append(_card_id)
                        self._fact_ids_in_queue.append(_fact_id)
                        non_memorised_in_queue += 1
                    if non_memorised_in_queue == limit:
                        break
            random.shuffle(self._card_ids_in_queue)
            # Only stop when we reach the non memorised limit. Otherwise, keep
            # going to add some extra cards to get more spread.
            if non_memorised_in_queue == limit:
                return
            # If the queue is empty, we can skip stage 2 in the future.
            if len(self._card_ids_in_queue) == 0:
                self.stage = 3

        # Stage 3
        #
        # Now do the cards which have never been committed to long-term
        # memory, but which we have seen before.
        # Use <= in the stage check, such that earlier stages can use
        # cards from this stage to increase the hand.
        if self.stage <= 3:
            for _card_id, _fact_id in db.cards_new_memorising(grade=1):
                if _fact_id not in self._fact_ids_in_queue:
                    if non_memorised_in_queue < limit:
                        self._card_ids_in_queue.append(_card_id)
                        self._fact_ids_in_queue.append(_fact_id)
                        non_memorised_in_queue += 1
                    if non_memorised_in_queue == limit:
                        break
            for _card_id, _fact_id in db.cards_new_memorising(grade=0):
                if _fact_id not in self._fact_ids_in_queue:
                    if non_memorised_in_queue < limit:
                        self._card_ids_in_queue.append(_card_id)
                        self._card_ids_in_queue.append(_card_id)
                        self._fact_ids_in_queue.append(_fact_id)
                        non_memorised_in_queue += 1
                    if non_memorised_in_queue == limit:
                        break
            random.shuffle(self._card_ids_in_queue)
            # Only stop when we reach the grade 0 limit. Otherwise, keep
            # going to add some extra cards to get more spread.
            if non_memorised_in_queue == limit:
                return
            # If the queue is empty, we can skip stage 3 in the future.
            if len(self._card_ids_in_queue) == 0:
                self.stage = 4

        # Stage 4
        #
        # Now add some cards we have yet to see for the first time.
        # Use <= in the stage check, such that earlier stages can use
        # cards from this stage to increase the hand.
        if self.stage <= 4:
            if self.config()["randomise_new_cards"]:
                sort_key = "random"
            else:
                sort_key = ""
            # Preferentially keep away from sister cards for as long as
            # possible.
            for _card_id, _fact_id in db.cards_unseen(\
                    sort_key=sort_key, limit=min(limit, 50)):
                if _fact_id not in self._fact_ids_in_queue \
                    and _fact_id not in self._fact_ids_memorised:
                    self._card_ids_in_queue.append(_card_id)
                    self._fact_ids_in_queue.append(_fact_id)
                    non_memorised_in_queue += 1
                    if non_memorised_in_queue == limit:
                        self.stage = 2
                        return
            # If the queue is close to empty, start pulling in sister cards.
            if len(self._fact_ids_in_queue) <= 2:
                for _card_id, _fact_id in db.cards_unseen(\
                        sort_key=sort_key, limit=min(limit, 50)):
                    if _fact_id not in self._fact_ids_in_queue:
                        self._card_ids_in_queue.append(_card_id)
                        self._fact_ids_in_queue.append(_fact_id)
                        non_memorised_in_queue += 1
                        if non_memorised_in_queue == limit:
                            self.stage = 2
                            return
            # If the queue is still empty, go to learn ahead of schedule.
            if len(self._card_ids_in_queue) == 0:
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
            self.stage = 2
            return
        for _card_id, _fact_id in db.cards_learn_ahead(self.adjusted_now(),
                sort_key="next_rep", limit=50):
            self._card_ids_in_queue.append(_card_id)
        # Relearn cards which we got wrong during learn ahead.
        self.stage = 2

    def is_in_queue(self, card):
        return card._id in self._card_ids_in_queue

    def remove_from_queue_if_present(self, card):
        try:
            self._card_ids_in_queue.remove(card._id)
            self._card_ids_in_queue.remove(card._id)
        except:
            pass

    def next_card(self, learn_ahead=False):
        db = self.database()
        # Populate queue if it is empty, and pop first card from the queue.
        if len(self._card_ids_in_queue) == 0:
            self.rebuild_queue(learn_ahead)
            if len(self._card_ids_in_queue) == 0:
                return None
        _card_id = self._card_ids_in_queue.pop(0)
        # Make sure we don't show the same card twice in succession.
        if self._card_id_last:
            while _card_id == self._card_id_last:
                # Make sure we have enough cards to vary, but exit in hopeless
                # situations.
                if len(self._card_ids_in_queue) == 0:
                    self.rebuild_queue(learn_ahead)
                    if len(self._card_ids_in_queue) == 0:
                        return None
                    if set(self._card_ids_in_queue) == set([_card_id]):
                        return db.card(_card_id, is_id_internal=True)
                _card_id = self._card_ids_in_queue.pop(0)
        self._card_id_last = _card_id
        return db.card(_card_id, is_id_internal=True)

    def is_prefetch_allowed(self, card_to_grade):

        """Can we display a new card before having processed the grading of
        the previous one?

        """

        # The grading of a card which previously had grade 0 will remove the
        # second copy from the queue in 'grade_answer', so we can't prefetch
        # if that second copy happens to be the one coming up.
        if self._card_ids_in_queue and \
            card_to_grade._id == self._card_ids_in_queue[0]:
            return False
        # Make sure there are enough cards left to find one which is not a
        # duplicate.
        return len(self._card_ids_in_queue) >= 3

    def interval_multiplication_factor(self, card, interval):

        """Allow plugin to easily scale the scheduled interval."""

        return 1.0

    def grade_answer(self, card, new_grade, dry_run=False):
        # The dry run mode is typically used to determine the intervals
        # for the different grades, so we don't want any side effects
        # from hooks running then.
        if not dry_run:
            for f in self.component_manager.all("hook", "before_repetition"):
                f.run(card)
        # When doing a dry run, make a copy to operate on. This leaves the
        # original in the GUI intact.
        if dry_run:
            import copy
            card = copy.copy(card)
        # Determine whether we learned on time or not (only relevant for
        # grades 2 or higher).
        if self.adjusted_now() - DAY >= card.next_rep: # Already due yesterday.
            timing = "LATE"
        else:
            if self.adjusted_now() < card.next_rep: # Not due today.
                timing = "EARLY"
            else:
                timing = "ON TIME"
        # Calculate the previously scheduled interval, i.e. the interval that
        # led up to this repetition.
        scheduled_interval = self.true_scheduled_interval(card)
        # If we memorise a card, keep track of its fact, so that we can avoid
        # pulling a sister card from the 'unseen' pile.
        if not dry_run and card.grade < 2 and new_grade >= 2:
            self._fact_ids_memorised.append(card.fact._id)
        if card.grade == -1: # Unseen card.
            actual_interval = 0
        else:
            actual_interval = int(self.stopwatch().start_time) - card.last_rep
        if card.grade == -1:
            # The card has not yet been given its initial grade.
            card.easiness = 2.5
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
            new_interval = self.calculate_initial_interval(new_grade)
        elif card.grade in [0, 1] and new_grade in [0, 1]:
            # In the acquisition phase and staying there.
            card.acq_reps += 1
            card.acq_reps_since_lapse += 1
            new_interval = 0
        elif card.grade in [0, 1] and new_grade in [2, 3, 4, 5]:
             # In the acquisition phase and moving to the retention phase.
             card.acq_reps += 1
             card.acq_reps_since_lapse += 1
             if new_grade == 2:
                 new_interval = DAY
             elif new_grade == 3:
                 new_interval = random.choice([1, 1, 2]) * DAY
             elif new_grade == 4:
                 new_interval = random.choice([1, 2, 2]) * DAY
             elif new_grade == 5:
                 new_interval = 2 * DAY
             # Make sure the second copy of a grade 0 card doesn't show
             # up again.
             if not dry_run and card.grade == 0:
                 if card._id in self._card_ids_in_queue:
                     self._card_ids_in_queue.remove(card._id)
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
            # Don't update the easiness when learning ahead.
            if timing in ["LATE", "ON TIME"]:
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
                    if timing in ["ON TIME", "EARLY"]:
                        new_interval = actual_interval * card.easiness
                    else:
                        # Learning late and interval was too long, so don't
                        # increase the interval and use scheduled_interval
                        # again as opposed to the much larger
                        # actual_interval * card.easiness.
                        new_interval = scheduled_interval
                if new_grade == 4:
                    new_interval = actual_interval * card.easiness
                if new_grade == 5:
                    if timing in ["EARLY"]:
                        # Learning ahead and interval was too short. To avoid
                        # that the intervals increase explosively when learning
                        # ahead, take scheduled_interval as opposed to the
                        # much larger actual_interval * card.easiness.
                        new_interval = scheduled_interval
                    else:
                        new_interval = actual_interval * card.easiness
                # Pathological case which can occur when learning ahead a card
                # in a single card database many times on the same day, such
                # that actual_interval becomes 0.
                if new_interval < DAY:
                    new_interval = DAY
        # Allow plugins to modify new_interval by multiplying it.
        new_interval *= self.interval_multiplication_factor(card, new_interval)
        new_interval = int(new_interval)
        # When doing a dry run, stop here and return the scheduled interval.
        if dry_run:
            return new_interval
        # Add some randomness to interval.
        new_interval += self.calculate_interval_noise(new_interval)
        # Update card properties. 'last_rep' is the time the card was graded,
        # not when it was shown.
        card.grade = new_grade
        card.last_rep = int(time.time())
        if new_grade >= 2:
            card.next_rep = self.midnight_UTC(card.last_rep + new_interval)
            self.avoid_sister_cards(card)
        else:
            card.next_rep = card.last_rep
        # Warn if we learned a lot of new cards.
        if len(self._fact_ids_memorised) == 15 and \
            self.warned_about_too_many_cards == False:
            self.main_widget().show_information(\
        _("You've memorised 15 new or failed cards.") + " " +\
        _("If you do this for many days, you could get a big workload later."))
            self.warned_about_too_many_cards = True       
        # Run hooks.
        self.database().current_criterion().apply_to_card(card)
        for f in self.component_manager.all("hook", "after_repetition"):
            f.run(card)
        # Create log entry.
        self.log().repetition(card, scheduled_interval, actual_interval,
            thinking_time=self.stopwatch().time())
        return new_interval

    def scheduled_count(self):
        return self.database().scheduled_count(self.adjusted_now())

    def non_memorised_count(self):
        return self.database().non_memorised_count()

    def active_count(self):
        return self.database().active_count()

    def card_count_scheduled_n_days_from_now(self, n):

        """Yesterday: n=-1, today: n=0, tomorrow: n=1, ... .

        Is not implemented in the database, because this could need internal
        scheduler information.
        """

        if n > 0:
            now = self.adjusted_now()
            return self.database().card_count_scheduled_between\
                    (now + (n - 1) * DAY, now + n * DAY)
        else:
            return self.database().card_count_scheduled_n_days_ago(-n)

    def next_rep_to_interval_string(self, next_rep, now=None):

        """Converts next_rep to a string like 'tomorrow', 'in 2 weeks', ...

        """

        if now is None:
            now = self.adjusted_now()
        interval_days = (next_rep - now) / DAY
        if interval_days >= 365:
            interval_years = interval_days/365.
            return _("in") + " " + "%.1f" % interval_years + " " + \
                   _("years")
        elif interval_days >= 62:
            interval_months = int(interval_days/31)
            return _("in") + " " + str(interval_months) + " " + \
                   _("months")
        elif interval_days >= 31:
            return _("in 1 month")
        elif interval_days >= 1:
            return _("in") + " " + str(int(interval_days) + 1) + " " + \
                   _("days")
        elif interval_days >= 0:
            return _("tomorrow")
        elif interval_days >= -1:
            return _("today")
        elif interval_days >= -2:
            return _("1 day overdue")
        elif interval_days >= -31:
            return str(int(-interval_days) - 1) + " " + _("days overdue")
        elif interval_days >= -62:
            return _("1 month overdue")
        elif interval_days >= -365:
            interval_months = int(-interval_days/31)
            return str(interval_months) + " " + _("months overdue")
        else:
            interval_years = -interval_days/365.
            return "%.1f " % interval_years +  _("years overdue")

    def last_rep_to_interval_string(self, last_rep, now=None):

        """Converts next_rep to a string like 'yesterday', '2 weeks ago', ...

        """

        if now is None:
            now = time.time()
        # To perform the calculation, we need to 'snap' the two timestamps
        # to midnight UTC before calculating the interval.
        now = self.midnight_UTC(\
            now - self.config()["day_starts_at"] * HOUR)
        last_rep = self.midnight_UTC(\
            last_rep - self.config()["day_starts_at"] * HOUR)
        interval_days = (last_rep - now) / DAY
        if interval_days > -1:
            return _("today")
        elif interval_days > -2:
            return _("yesterday")
        elif interval_days > -31:
            return str(int(-interval_days)) + " " + _("days ago")
        elif interval_days > -62:
            return _("1 month ago")
        elif interval_days > -365:
            interval_months = int(-interval_days/31.)
            return str(interval_months) + " " + _("months ago")
        else:
            interval_years = -interval_days/365.
            return "%.1f " % interval_years +  _("years ago")

