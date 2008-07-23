##############################################################################
#
# card.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import md5, time, logging

from mnemosyne.libmnemosyne.plugin_manager import *

#from mnemosyne.libmnemosyne.card_type import *
from mnemosyne.libmnemosyne.start_date import start_date
#from mnemosyne.libmnemosyne.scheduler import *
#from mnemosyne.libmnemosyne.database import *

log = logging.getLogger("mnemosyne")




##############################################################################
#
# Card
#
# We store q and a in strings to cache them, instead of regenerating them
# each time from its Fact. This could take too much time, e.g. on a mobile
# platform. Also useful for searching in sql database
#
# 'subcard' indicate different cards generated from the same fact data,
# like reverse cards. TODO: do we need a mapping from this integer to a
# description?
#
# If the user deletes a subcard from a fact, we don't delete it, in case
# the user later reactivates it. We can either employ a 'hidden'
# variable here, or move it to a different container (perhaps more
# efficient?). TODO: implement and benchmark
#
##############################################################################

class Card(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
            
    def __init__(self, grade, card_type, fact, subcard, cat_names, id=None):

        db = get_database()
        sch = get_scheduler()

        self.card_type = card_type
        self.fact      = fact
        self.subcard   = subcard
        self.q         = self.filtered_q()
        self.a         = self.filtered_a()
        self.hidden    = False

        self.cat = []
        for cat_name in cat_names:
            self.cat.append(db.get_or_create_category_with_name(cat_name))
        
        self.reset_learning_data() # TODO: see where this is used and merge.

        # The initial grading is seen as the first repetition.
        
        self.grade = grade
        self.acq_reps = 1
        self.acq_reps_since_lapse = 1

        self.last_rep = start_date.days_since_start()

        self.easiness = db.average_easiness()

        if id == None:
            self.new_id()
        else:
            self.id = id 

        new_interval  = sch.calculate_initial_interval(grade)
        new_interval += sch.calculate_interval_noise(new_interval)
        self.next_rep = start_date.days_since_start() + new_interval

        

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
    # save
    #
    ##########################################################################
    
    def save(self):

        get_database().add_card(self)

        new_interval = start_date.days_since_start() - self.next_rep

        log.info("New card %s %d %d", self.id, self.grade, new_interval)

        print 'new card', self.q, self.a


        
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
    # is_in_active_category
    #
    ##########################################################################

    def is_in_active_category(self):
        
        for c in self.cat:
            if c.active == False:
                return False
            
        return True
    

# TODO: see which of these we still need and if they could be moved to
# database

    
    
    ##########################################################################
    #
    # is_new
    #
    ##########################################################################
    
    def is_new(self):
        return (self.acq_reps == 0) and (self.ret_reps == 0)
    
    
    
    ##########################################################################
    #
    # is_overdue
    #
    ##########################################################################
    
    def is_overdue(self):
        return (self.grade >= 2) and (self.is_in_active_category()) and \
               (days_since_start > self.next_rep)

    ##########################################################################
    #
    # days_since_last_rep
    #
    ##########################################################################
    
    def days_since_last_rep(self):
        return days_since_start - self.last_rep

    ##########################################################################
    #
    # days_until_next_rep
    #
    ##########################################################################
    
    def days_until_next_rep(self):
        return self.next_rep - days_since_start
    

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
