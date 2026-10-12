#
# fixed_intervals.py
#

import time

from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne import \
     SM2Mnemosyne, HOUR, DAY


class FixedIntervals(SM2Mnemosyne):

    """Scheduler with fixed intervals, no easiness factor:

        grade 0 -> start of the next day (per 'day_starts_at'), placed first
                   among the cards due at that time
        grade 1 -> +3 days, 2 -> +7, 3 -> +15, 4 -> +30, 5 -> +60

    All seen cards form a single rolling queue sorted by due time
    ('next_rep'). Ties are broken by putting grade 0 cards first, and then by
    the moment of grading ('last_rep', then '_id'), so that cards keep the
    order in which they were graded. Overdue cards simply stay in the queue,
    in the same priority order. Unseen cards come after all due cards.

    As in SM2Mnemosyne, 'next_rep' is stored as midnight UTC of the target
    (local) day, and 'day_starts_at' is taken into account when querying.

    """

    name = "Fixed intervals"

    INTERVAL_DAYS = (1, 3, 7, 15, 30, 60)

    def interval_days(self, grade):
        return self.INTERVAL_DAYS[grade]

    def next_rep_for(self, grade, timestamp):
        # Shift by 'day_starts_at', so that e.g. grading at 01:00 with a day
        # start of 03:00 still counts as the previous day, and grade 0 becomes
        # due at 03:00 that same morning, i.e. the start of the next day.
        local_day = timestamp - self.config()["day_starts_at"] * HOUR
        return self.midnight_UTC(local_day + self.interval_days(grade) * DAY)

    def true_scheduled_interval(self, card):
        interval = card.next_rep - card.last_rep
        interval += self.config()["day_starts_at"] * HOUR
        if time.localtime(time.time()).tm_isdst and time.daylight:
            interval += time.altzone
        else:
            interval += time.timezone
        return int(interval)

    def set_initial_grade(self, cards, grade):
        last_rep = int(time.time())
        next_rep = self.next_rep_for(grade, last_rep)
        for card in cards:
            card.grade = grade
            card.easiness = 2.5
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
            card.last_rep = last_rep
            card.next_rep = next_rep
            self.log().repetition(card, scheduled_interval=0,
                actual_interval=0, thinking_time=0)

    def _ordered_due_cards(self, timestamp, limit=-1):
        return ((cursor[0], cursor[1]) for cursor in \
            self.database().con.execute("""
            select _id, _fact_id from cards where active=1 and grade>=0
            and ?>=next_rep order by next_rep, (grade!=0), last_rep, _id
            limit ?""", (timestamp, limit)))

    def _ordered_upcoming_cards(self, timestamp, limit=-1):
        return ((cursor[0], cursor[1]) for cursor in \
            self.database().con.execute("""
            select _id, _fact_id from cards where active=1 and grade>=0
            and ?<next_rep order by next_rep, (grade!=0), last_rep, _id
            limit ?""", (timestamp, limit)))

    def rebuild_queue(self, learn_ahead=False):
        db = self.database()
        if not db.is_loaded() or not db.active_count():
            return
        self._card_ids_in_queue = []
        self._fact_ids_in_queue = []
        now = self.adjusted_now()
        # Due and overdue cards, in strict priority order.
        if not self.new_only:
            for _card_id, _fact_id in self._ordered_due_cards(now, limit=50):
                self._card_ids_in_queue.append(_card_id)
                self._fact_ids_in_queue.append(_fact_id)
            if self._card_ids_in_queue:
                return
        # New cards.
        sort_key = "random" if self.config()["randomise_new_cards"] else ""
        limit = self.config()["non_memorised_cards_in_hand"]
        for _card_id, _fact_id in db.cards_unseen(\
                sort_key=sort_key, limit=min(limit, 50)):
            if _fact_id not in self._fact_ids_in_queue:
                self._card_ids_in_queue.append(_card_id)
                self._fact_ids_in_queue.append(_fact_id)
        if self._card_ids_in_queue or not learn_ahead:
            return
        # Learn ahead: upcoming cards in the same priority order.
        for _card_id, _fact_id in self._ordered_upcoming_cards(now, limit=50):
            self._card_ids_in_queue.append(_card_id)
            self._fact_ids_in_queue.append(_fact_id)

    def remove_from_queue_if_present(self, card):
        while card._id in self._card_ids_in_queue:
            self._card_ids_in_queue.remove(card._id)

    def next_card(self, learn_ahead=False):
        # A graded card is always rescheduled to a later day, so the queue
        # never contains the just graded card twice; keep strict order.
        db = self.database()
        if len(self._card_ids_in_queue) == 0:
            self.rebuild_queue(learn_ahead)
            if len(self._card_ids_in_queue) == 0:
                return None
        _card_id = self._card_ids_in_queue.pop(0)
        self._card_id_last = _card_id
        return db.card(_card_id, is_id_internal=True)

    def is_prefetch_allowed(self, card_to_grade):
        return False

    def grade_answer(self, card, new_grade, dry_run=False):
        if not dry_run:
            for f in self.component_manager.all("hook", "before_repetition"):
                f.run(card)
        if dry_run:
            import copy
            card = copy.copy(card)
        scheduled_interval = self.true_scheduled_interval(card) \
            if card.grade >= 0 else 0
        if card.grade == -1:
            actual_interval = 0
        else:
            actual_interval = int(self.stopwatch().start_time) - card.last_rep
        # Keep the statistics counters meaningful.
        if card.grade == -1:
            card.easiness = 2.5
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
        elif card.grade < 2 and new_grade < 2:
            card.acq_reps += 1
            card.acq_reps_since_lapse += 1
        elif card.grade < 2 and new_grade >= 2:
            card.acq_reps += 1
            card.acq_reps_since_lapse += 1
        elif card.grade >= 2 and new_grade < 2:
            card.ret_reps += 1
            card.lapses += 1
            card.acq_reps_since_lapse = 0
            card.ret_reps_since_lapse = 0
        else:
            card.ret_reps += 1
            card.ret_reps_since_lapse += 1
        now = int(time.time())
        if not dry_run:
            # Guarantee strictly increasing grading timestamps, so that
            # 'last_rep' preserves grading order even within one second.
            latest = self.database().con.execute("""select max(last_rep)
                from cards""").fetchone()[0] or 0
            if now <= latest and latest - now < 60:
                now = latest + 1
        next_rep = self.next_rep_for(new_grade, now)
        new_interval = int(next_rep - now)
        if dry_run:
            return self.interval_days(new_grade) * DAY
        card.grade = new_grade
        card.last_rep = now
        card.next_rep = next_rep
        self.remove_from_queue_if_present(card)
        self.database().current_criterion().apply_to_card(card)
        for f in self.component_manager.all("hook", "after_repetition"):
            f.run(card)
        self.log().repetition(card, scheduled_interval, actual_interval,
            thinking_time=self.stopwatch().time())
        return new_interval

    def scheduled_count(self):
        return self.database().con.execute("""select count() from cards
            where active=1 and grade>=0 and ?>=next_rep""",
            (self.adjusted_now(), )).fetchone()[0]
