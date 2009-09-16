#
# cramming.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne import SM2Mnemosyne


class Cramming(SM2Mnemosyne):

    UNSEEN = 0
    WRONG = 1
    RIGHT = 2

    name = "cramming"

    def reset(self):
        SM2Mnemosyne.reset(self)
        if self.database().is_loaded():
            self.database().set_scheduler_data(self.UNSEEN)

    def rebuild_queue(self, learn_ahead=False):
        self.card__ids_in_queue = []
        self.fact__ids_in_queue = []
        db = self.database()

        if not db.is_loaded() or not db.active_count():
            return

        # Stage 1 : do all the unseen cards.     
        if self.stage == 1:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.UNSEEN,
                                      sort_key="random", limit=25):
                if _fact_id not in self.fact__ids_in_queue:
                    self.card__ids_in_queue.append(_card_id)
                    self.fact__ids_in_queue.append(_fact_id)
            if len(self.card__ids_in_queue):
                return
            self.stage = 2

        # Stage 2: do the cards we got wrong.
        if self.stage == 2:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.WRONG,
                                      sort_key="random", limit=25):
                if _fact_id not in self.fact__ids_in_queue:
                    self.card__ids_in_queue.append(_card_id)
                    self.fact__ids_in_queue.append(_fact_id)
            if len(self.card__ids_in_queue):
                return
            
        # Start again.
        self.reset()
        self.rebuild_queue()

    def grade_answer(self, card, new_grade, dry_run=False):
        # The dry run mode is typically used to determine the intervals
        # for the different grades, so we don't want any side effects
        # from hooks running then.
        if not dry_run:
            card.fact.card_type.before_repetition(card)
            for f in self.component_manager.get_all("hook",
                                                    "before_repetition"):
                f.run(card)
        # Do the actual grading.       
        if new_grade <= 1:
            card.scheduler_data = self.WRONG
        else:
            card.scheduler_data = self.RIGHT
        # Run hooks.
        card.fact.card_type.after_repetition(card)
        for f in self.component_manager.get_all("hook", "after_repetition"):
            f.run(card)
        return 0
