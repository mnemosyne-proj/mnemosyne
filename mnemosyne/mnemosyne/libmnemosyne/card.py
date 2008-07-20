##############################################################################
#
# card.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import md5, time, logging

from mnemosyne.libmnemosyne.category import *
from mnemosyne.libmnemosyne.card_type import *
from mnemosyne.libmnemosyne.start_date import get_days_since_start
from mnemosyne.libmnemosyne.scheduler import *
from mnemosyne.libmnemosyne.database import *

logger = logging.getLogger("mnemosyne")

db = get_database()



##############################################################################
#
# Card
#
# q and a: store strings with basic / cached q and a? In case generating
# it each time from the data takes to much time, e.g. on a mobile platform.
# Also useful for searching in sql database
#
# 'subcard' indicate different cards generated from the same fact data,
# like reverse cards.
#
##############################################################################

class Card(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.id = 0

        self.card_type = None

        self.fact = None

        self.subcard = 0 # Integer instead of string to save space.

        # TODO: do we need a mapping from this integer to a description?

        # If the user deletes a subcard from a fact, we don't delete it, in
        # case the user later reactivates it. We can either employ a 'hidden'
        # variable here, or move it to a different container (perhaps more
        # efficient?)

        self.hidden = False # TODO
        
        self.q   = None
        self.a   = None
        self.cat = []
        
        self.reset_learning_data()

    ##########################################################################
    #
    # filtered_q
    #
    ##########################################################################

    def filtered_q(self):

        q = self.card_type.generate_q(self.fact, self.subcard)

        #q = preprocess(q) # TODO: update to plugin scheme

        return q

    ##########################################################################
    #
    # filtered_a
    #
    ##########################################################################
    
    def filtered_a(self):
        
        a = self.card_type.generate_a(self.fact, self.subcard)

        #a = preprocess(a) # TODO: update to plugin scheme

        return a
    
    
    ##########################################################################
    #
    # reset_learning_data
    #
    ##########################################################################

    def reset_learning_data(self):

        self.grade                = 0
        self.easiness             = 2.5
        
        self.acq_reps             = 0
        self.ret_reps             = 0
        self.lapses               = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0

        # TODO: store as float for minute level scheduling
        
        self.last_rep  = 0 # In days since beginning.
        self.next_rep  = 0 #

    ##########################################################################
    #
    # new_id
    #
    ##########################################################################
    
    def new_id(self):

        digest = md5.new(self.q.encode("utf-8") + self.a.encode("utf-8") + \
                         time.ctime()).hexdigest()
        self.id = digest[0:8]
        
    ##########################################################################
    #
    # sort_key
    #
    ##########################################################################

    def sort_key(self):
        return self.next_rep
    
    ##########################################################################
    #
    # sort_key_interval
    #
    ##########################################################################

    def sort_key_interval(self):
        return self.next_rep-self.last_rep
    
    ##########################################################################
    #
    # sort_key_newest
    #
    ##########################################################################

    def sort_key_newest(self):
        return self.acq_reps + self.ret_reps
    
    ##########################################################################
    #
    # is_new
    #
    ##########################################################################
    
    def is_new(self):
        return (self.acq_reps == 0) and (self.ret_reps == 0)
    
    ##########################################################################
    #
    # is_due_for_acquisition_rep
    #
    ##########################################################################
    
    def is_due_for_acquisition_rep(self):
        return (self.grade < 2) and (self.is_in_active_category())
    
    ##########################################################################
    #
    # is_due_for_retention_rep
    #
    #  Due for a retention repetion within 'days' days?
    #
    ##########################################################################
    
    def is_due_for_retention_rep(self, days=0):
        return (self.grade >= 2) and (self.is_in_active_category()) and \
               (get_days_since_start() >= self.next_rep - days)
    
    ##########################################################################
    #
    # is_overdue
    #
    ##########################################################################
    
    def is_overdue(self):
        return (self.grade >= 2) and (self.is_in_active_category()) and \
               (get_days_since_start() > self.next_rep)

    ##########################################################################
    #
    # days_since_last_rep
    #
    ##########################################################################
    
    def days_since_last_rep(self):
        return get_days_since_start() - self.last_rep

    ##########################################################################
    #
    # days_until_next_rep
    #
    ##########################################################################
    
    def days_until_next_rep(self):
        return self.next_rep - get_days_since_start()
    
    ##########################################################################
    #
    # is_in_active_category
    #
    ##########################################################################

    def is_in_active_category(self):
        
        for c in self.cat:
            if c.active == False:
                return False
            
        return True

    ##########################################################################
    #
    # qualifies_for_learn_ahead
    #
    ##########################################################################
    
    def qualifies_for_learn_ahead(self):
        return (self.grade >= 2) and (self.is_in_active_category()) and \
               (get_days_since_start() < self.next_rep) 
        
    ##########################################################################
    #
    # change_category
    #
    ##########################################################################
    
    def change_category(self, new_cat_name):

        old_cat = self.cat
        self.cat = get_category_by_name(new_cat_name)
        remove_category_if_unused(old_cat)




# TODO: see how to move this best to the above claas.

##############################################################################
#
# add_new_card
#
##############################################################################

def add_new_card(grade, card_type_id, fact, subcard, cat_names, id=None):

    global cards, load_failed

    card = Card()
    
    card.card_type = get_card_type_by_id(card_type_id)  
    card.fact      = fact
    card.subcard   = subcard   
    card.q         = card.filtered_q()
    card.a         = card.filtered_a()
    card.grade     = grade

    for cat_name in cat_names:
        card.cat.append(get_category_by_name(cat_name))
    
    card.acq_reps = 1
    card.acq_reps_since_lapse = 1

    card.last_rep = get_days_since_start()
    
    card.easiness = average_easiness()

    if id == None:
        card.new_id()
    else:
        card.id = id 
    
    new_interval  = calculate_initial_interval(grade)
    new_interval += calculate_interval_noise(new_interval)
    card.next_rep = get_days_since_start() + new_interval

    db.add_card(card)

    logger.info("New card %s %d %d", card.id, card.grade, new_interval)

    load_failed = False # TODO: check?

    print 'new card', card.q, card.a
    
    return card
