#
# cramming.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne import SM2Mnemosyne


class Cramming(SM2Mnemosyne):

    UNSEEN = 0
    WRONG = 1
    RIGHT = 2

    name = "cramming"

    def reset(self):
        SM2Mnemosyne.reset(self)
        database().set_scheduler_data(self.UNSEEN)

    def rebuild_queue(self, learn_ahead=False):
        self.queue = []
        self.facts = []
        db = database()
        if not db.is_loaded():
            return
         
        # Stage 1 : do all the unseen cards.     
        if self.stage == 1:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.UNSEEN,
                                      sort_key="random", limit=25):
                if _fact_id not in self.facts:
                    self.queue.append(_card_id)
                    self.facts.append(_fact_id)
            if len(self.queue):
                return
            self.stage = 2

        # Stage 2: do the cards we got wrong.
        if self.stage == 2:
            for _card_id, _fact_id in db.cards_with_scheduler_data(self.WRONG,
                                      sort_key="random", limit=25):
                if _fact_id not in self.facts:
                    self.queue.append(_card_id)
                    self.facts.append(_fact_id)
            if len(self.queue):
                return
            
        # Start again.
        self.reset()
        self.rebuild_queue()

    def grade_answer(self, card, new_grade, dry_run=False):
        if new_grade <= 1:
            card.scheduler_data = self.WRONG
        else:
            card.scheduler_data = self.RIGHT
        return 0


class CrammingPlugin(Plugin):

    name = _("Cramming scheduler")
    description = \
  _("Goes through cards in random order without saving scheduling information.")

    def __init__(self):
        Plugin.__init__(self, [Cramming()])
