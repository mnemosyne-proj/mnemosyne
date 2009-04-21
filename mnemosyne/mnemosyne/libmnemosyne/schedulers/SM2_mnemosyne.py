#
# SM2_mnemosyne.py <Peter.Bienstman@UGent.be>
#

import random
import copy

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.scheduler import Scheduler
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.component_manager import database, config, log


# Scheduler based on http://www.supermemo.com/english/ol/sm2.htm.

class SM2Mnemosyne(Scheduler):
    
    name = "SM2 Mnemosyne"
    
    def __init__(self):
        self.queue = []
        
    def set_initial_grade(self, card, grade):

        """Called when cards are given their initial grade outside of the
        review process, e.g. when the user gives an initial grade when
        adding a new card in the GUI. Therefore, 'unseen' is still left to
        True, as this card has not yet been seen in the interactive review
        process.

        Cards which don't have initial grade information available (e.g. for
        cards created during import or conversion from different card type),
        get their initial grade when they are encountered in the interactive
        review process for the first time.
        
        In both cases, this initial grading is seen as the first repetition.

        In this way, both types of cards are treated in the same way. (There
        is an ineffectual asymmetry left in the log messages they generate,
        but all the relevant information can still be parsed from them.)

        """
                
        db = database()
        card.grade = grade
        card.easiness = db.average_easiness()
        card.acq_reps = 1
        card.acq_reps_since_lapse = 1
        card.last_rep = db.days_since_start()
        new_interval = self.calculate_initial_interval(grade)
        new_interval += self.calculate_interval_noise(new_interval)
        card.next_rep = card.last_rep + new_interval

    def calculate_initial_interval(self, grade):
        
        """The first repetition is treated specially, and gives longer
        intervals, to allow for the fact that the user may have seen this
        card before.

        """
        
        interval = (0, 0, 1, 3, 4, 5) [grade]
        return interval

    def calculate_interval_noise(self, interval):
        if interval == 0:
            noise = 0
        elif interval == 1:
            noise = random.randint(0,1)
        elif interval <= 10:
            noise = random.randint(-1,1)
        elif interval <= 60:
            noise = random.randint(-3,3)
        else:
            a = .05 * interval
            noise = round(random.uniform(-a,a))
        return noise

    def rebuild_queue(self, learn_ahead=False):
        self.queue = []
        ui_controller_review().clear()
        db = database()
        if not db.is_loaded():
            return
        # Do the cards that are scheduled for today (or are overdue), but
        # first do those that have the shortest interval, as being a day
        # late on an interval of 2 could be much worse than being a day late
        # on an interval of 50.
        # Get only one card at the time, and let repeated calls to
        # 'rebuild_queue' do the rest.
        try:
            self.queue = [db.cards_due_for_ret_rep(sort_key="interval").next()]
            return
        except:
            pass
        # Now rememorise the cards that we got wrong during the last stage.
        # Concentrate on only a limited number of grade 0 cards, in order to
        # avoid too long intervals between repetitions. If there are too few
        # cards left in the queue, append more new cards to keep some
        # spread between these last cards.
        limit = config()["grade_0_items_at_once"]
        grade_0 = db.cards_due_for_final_review(grade=0, sort_key="random")
        grade_0_selected = []
        if limit != 0:
            for i in grade_0:
                # TODO: won't these show up later the same day?
                for j in grade_0_selected:
                    if i.fact == j.fact:
                        break
                else:
                    grade_0_selected.append(i)
                if len(grade_0_selected) == limit:
                    break
        grade_1 = list(db.cards_due_for_final_review(grade=1,
                                                     sort_key="random"))
        self.queue += 2*grade_0_selected + grade_1
        random.shuffle(self.queue)
        if limit and len(grade_0_selected) == limit:
            return
        # Now do the cards which have never been committed to long-term
        # memory, but which we have seen before.
        grade_0 = db.cards_new_memorising(grade=0, sort_key="random")
        grade_0_in_queue = len(grade_0_selected)
        grade_0_selected = []
        if limit != 0:
            for i in grade_0:
                for j in grade_0_selected:
                    if i.fact == j.fact:
                        break
                else:
                    grade_0_selected.append(i)
                if len(grade_0_selected) + grade_0_in_queue == limit:
                    break
        grade_1 = list(db.cards_new_memorising(grade=1, sort_key="random"))
        self.queue += 2*grade_0_selected + grade_1
        random.shuffle(self.queue)
        if limit and len(grade_0_selected) + grade_0_in_queue == limit:
            return
        # Now add some unseen cards.
        if config()["randomise_new_cards"]:
            sort_key = "random"
        else:
            sort_key = ""
        unseen = db.cards_unseen(sort_key=sort_key)
        grade_0_in_queue = sum(1 for i in self.queue if i.grade == 0)/2
        grade_0_selected = []
        try:
            while True:
                new_card = unseen.next()
                for i in grade_0_selected:
                    if new_card.fact == i.fact:
                        break
                else:
                    grade_0_selected.append(new_card)
                if limit and len(grade_0_selected) + grade_0_in_queue == limit:
                    raise StopIteration
        except StopIteration:
            self.queue += grade_0_selected
        if len(self.queue):
            return
        # If we get to here, there are no more scheduled cards or new cards
        # to learn. The user can signal that he wants to learn ahead by
        # calling rebuild_queue with 'learn_ahead' set to True.
        # Don't shuffle this queue, as it's more useful to review the
        # earliest scheduled cards first. We only put 5 cards at the same
        # time into the queue, in order to save memory.
        # TODO: this requires the user to click 'learn ahead of schedule'
        # again after 5 cards. If it's possible to make this algorithm
        # stateless and return 1 card at the time, this will be solved
        # automatically.
        # Note: this will not revisit failed cards when learning ahead.
        if learn_ahead == False:
            return
        else:
            for card in db.cards_learn_ahead(sort_key="next_rep"):
                self.queue.append(card)
                if len(self.queue) >= 5:
                    return

    def in_queue(self, card):
        return card in self.queue

    def remove_from_queue(self, card):

        """Remove a single instance of a card from the queue. Necessary when
        the queue needs to be rebuilt, and there is still a question pending.

        """

        for i in self.queue:
            if i.id == card.id:
                self.queue.remove(i)
                return

    def get_next_card(self, learn_ahead=False):
        # Populate queue if it is empty.
        if len(self.queue) == 0:
            self.rebuild_queue(learn_ahead)
            if len(self.queue) == 0:
                return None
        # Pick the first card and remove it from the queue.
        card = self.queue[0]
        self.queue.remove(card)
        return card

    def process_answer(self, card, new_grade, dry_run=False):
        db = database()
        days_since_start = db.days_since_start()
        # When doing a dry run, make a copy to operate on. Note that this
        # leaves the original in cards and the reference in the GUI intact.
        if dry_run:
            card = copy.copy(card)
        # Calculate scheduled and actual interval, taking care of corner
        # case when learning ahead on the same day.
        scheduled_interval = card.next_rep - card.last_rep
        actual_interval = days_since_start - card.last_rep
        if actual_interval == 0:
            actual_interval = 1 # Otherwise new interval can become zero.
        if (card.acq_reps == 0) and (card.ret_reps == 0):
            # The card has not yet been given its initial grade, because it
            # was imported or created during card type conversion.
            card.easiness = db.average_easiness()
            card.acq_reps = 1
            card.acq_reps_since_lapse = 1
            new_interval = self.calculate_initial_interval(new_grade)
            # Make sure the second copy of a grade 0 card doesn't show
            # up again.
            if not dry_run and card.grade == 0 and new_grade in [2,3,4,5]:
                for i in self.queue:
                    if i.id == card.id:
                        self.queue.remove(i)
                        break
        elif card.grade in [0,1] and new_grade in [0,1]:
            # In the acquisition phase and staying there.
            card.acq_reps += 1
            card.acq_reps_since_lapse += 1
            new_interval = 0
        elif card.grade in [0,1] and new_grade in [2,3,4,5]:
             # In the acquisition phase and moving to the retention phase.
             card.acq_reps += 1
             card.acq_reps_since_lapse += 1
             new_interval = 1
             # Make sure the second copy of a grade 0 card doesn't show
             # up again.
             if not dry_run and card.grade == 0:
                 for i in self.queue:
                     if i.id == card.id:
                         self.queue.remove(i)
                         break
        elif card.grade in [2,3,4,5] and new_grade in [0,1]:
             # In the retention phase and dropping back to the
             # acquisition phase.
             card.ret_reps += 1
             card.lapses += 1
             card.acq_reps_since_lapse = 0
             card.ret_reps_since_lapse = 0
             new_interval = 0
        elif card.grade in [2,3,4,5] and new_grade in [2,3,4,5]:
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
            new_interval = 0
            if card.ret_reps_since_lapse == 1:
                new_interval = 6
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
            # Shouldn't happen, but build in a safeguard.
            if new_interval == 0:
                print "Internal error: new interval was zero."
                new_interval = scheduled_interval
            new_interval = int(new_interval)
        # When doing a dry run, stop here and return the scheduled interval.
        if dry_run:
            return new_interval
        # Add some randomness to interval.
        noise = self.calculate_interval_noise(new_interval)
        # Update grade and interval.
        card.grade = new_grade
        card.last_rep = days_since_start
        card.next_rep = days_since_start + new_interval + noise
        card.unseen = False
        # Don't schedule related cards on the same day.
        for c in db.cards_from_fact(card.fact):
            if c != card and c.next_rep == card.next_rep and card.grade >= 2:
                card.next_rep += 1
                noise += 1
        db.update_card(card)
        # Run post review hooks.
        card.fact.card_type.after_review(card)
        # Create log entry.
        log().revision(card, scheduled_interval, actual_interval,
                       new_interval, noise)
        return new_interval + noise

    def clear_queue(self):
        self.queue = []
