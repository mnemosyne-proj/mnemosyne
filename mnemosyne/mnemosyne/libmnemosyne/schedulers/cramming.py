#
# cramming.py <Peter.Bienstman@UGent.be>
#

import copy

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.scheduler.SM2_mnemosyne import SM2Mnemos
from mnemosyne.libmnemosyne.component_manager import database, config, log


# Scheduler based on http://www.supermemo.com/english/ol/sm2.htm.

class Cramming(SM2Mnemosyne, Plugin):

    """Note: we inherit from the SM2 scheduler in order to use e.g. its
    'set_initial_grade' function. Otherwise we would not be able to add new
    cards while using this scheduler.

    """

    provides = "scheduler"

    def __init__(self):
        CardType.__init__(self)
        self.name = _("Cramming scheduler")
        self.description = \
 _("Goes through cards in random order without saving scheduling information.")

    def reset(self):
        self.queue = []

    def rebuild_queue(self, learn_ahead=False):
        self.queue = []
        self.facts = []
        db = database()
        if not db.is_loaded():
            return

    def in_queue(self, card): # same
        return card._id in self.queue
    
    def remove_from_queue(self, card): # same
        try:
            self.queue.remove(card._id)
            self.queue.remove(card._id)
        except:
            pass
    
    def get_next_card(self, learn_ahead=False): # same
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
        return database().get_card(_card_id)

    def allow_prefetch(self): # same

        """Can we display a new card before having processed the grading of
        the previous one?.

        """
                
        # Make sure there are enough cards left to find one which is not a
        # duplicate.
        return len(self.queue) >= 3

    def grade_answer(self, card, new_grade, dry_run=False):
        db = database()
        
