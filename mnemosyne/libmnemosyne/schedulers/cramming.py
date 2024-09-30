#
# cramming.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne import SM2Mnemosyne

RANDOM = 0
EARLIEST_FIRST = 1
LATEST_FIRST = 2
MOST_LAPSES_FIRST = 3


class Cramming(SM2Mnemosyne):

    UNSEEN = 0
    WRONG = 1
    RIGHT = 2

    name = "cramming"

    def __init__(self, component_manager):
        SM2Mnemosyne.__init__(self, component_manager)
        self.first_run = True

    def reset(self, new_only=False):
        if self.first_run and self.config()["cramming_store_state"] == False:
            self.database().set_scheduler_data(self.UNSEEN)
        self.first_run = False
        SM2Mnemosyne.reset(self, new_only)
        self.stage = 1

    def rebuild_queue(self, learn_ahead=False):
        db = self.database()
        if not db.is_loaded() or not db.active_count():
            return
        max_ret_reps = self.config()["max_ret_reps_for_recent_cards"] \
            if self.new_only else -1
        if self.new_only and db.recently_memorised_count(max_ret_reps) == 0:
            return
        self._card_ids_in_queue = []
        self._fact_ids_in_queue = []
        self.criterion = db.current_criterion()
        # Determine sort key.
        if self.config()["cramming_order"] == RANDOM:
            sort_key = "random"
        elif self.config()["cramming_order"] == EARLIEST_FIRST:
            sort_key = "next_rep"
        elif self.config()["cramming_order"] == LATEST_FIRST:
            sort_key = "next_rep desc"
        elif self.config()["cramming_order"] == MOST_LAPSES_FIRST:
            sort_key = "lapses desc"
        # Stage 1: do all the unseen cards.
        if self.stage == 1:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.UNSEEN,
                    sort_key=sort_key, limit=25, max_ret_reps=max_ret_reps):
                if _fact_id not in self._fact_ids_in_queue:
                    self._card_ids_in_queue.append(_card_id)
                    self._fact_ids_in_queue.append(_fact_id)
            if len(self._card_ids_in_queue):
                return
            self.stage = 2
        # Stage 2: do the cards we got wrong.
        if self.stage == 2:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.WRONG,
                    sort_key=sort_key, limit=25, max_ret_reps=max_ret_reps):
                if _fact_id not in self._fact_ids_in_queue:
                    self._card_ids_in_queue.append(_card_id)
                    self._fact_ids_in_queue.append(_fact_id)
            if len(self._card_ids_in_queue):
                return
        # Start again.
        self.database().set_scheduler_data(self.UNSEEN)
        self.stage = 1
        self.rebuild_queue()

    def grade_answer(self, card, new_grade, dry_run=False):
        # The dry run mode is typically used to determine the intervals
        # for the different grades, so we don't want any side effects
        # from hooks running then.
        if not dry_run:
            for f in self.component_manager.all("hook", "before_repetition"):
                f.run(card)
        # Do the actual grading.
        if new_grade <= 1:
            card.scheduler_data = self.WRONG
        else:
            card.scheduler_data = self.RIGHT
        # Run hooks.
        self.criterion.apply_to_card(card)
        for f in self.component_manager.all("hook", "after_repetition"):
            f.run(card)
        return 0