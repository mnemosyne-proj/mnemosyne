##############################################################################
#
# card.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import md5, time

from mnemosyne.libmnemosyne.plugin_manager import get_database, get_scheduler



##############################################################################
#
# Card
#
# Note that we store a card_type_id, as opposed to a card_type, because
# otherwise we can't use pickled databases, as the card_types themselves are
# not stored in the database. It is also closer the SQL implementation.
#
# 'fact_view' indicate different cards generated from the same fact data,
# like reverse cards. TODO: do we need a mapping from this integer to a
# description?
#
# For UI simplicity reasons, the user is not allowed to deleted one of a set
# of related cards, only to deactivate them. This is a second, orthogonal
# selection mechanism to see if cards are active, together with not being
# in a deactivated category.
#
##############################################################################

class Card(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
            
    def __init__(self, grade, card_type, fact, fact_view, cat_names, id=None):

        self.card_type_id = card_type.id
        self.fact         = fact
        self.fact_view    = fact_view
        self.active       = True

        db = get_database()

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

        if id is not None:
            self.new_id()
        else:
            self.id = id

        sch = get_scheduler()
        
        new_interval  = sch.calculate_initial_interval(grade)
        new_interval += sch.calculate_interval_noise(new_interval)
        self.next_rep = start_date.days_since_start() + new_interval

        

    ##########################################################################
    #
    # question
    #
    ##########################################################################

    def question(self):

        card_type = get_card_type_by_id(self.card_type_id)

        q = card_type.generate_q(self.fact, self.fact_view)

        #q = preprocess(q) # TODO: update to plugin scheme

        return q



    ##########################################################################
    #
    # answer
    #
    ##########################################################################
    
    def answer(self):
        
        card_type = get_card_type_by_id(self.card_type_id)
        
        a = card_type.generate_a(self.fact, self.fact_view)

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

        # TODO: store as float for minute level scheduling.
        
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
    # interval
    #
    ##########################################################################

    def interval(self):
        return self.next_rep - self.last_rep
    
        
    ##########################################################################
    #
    # sort_key: needed?
    #
    ##########################################################################

    def sort_key(self):
        return self.next_rep
    

    
    ##########################################################################
    #
    # sort_key_newest: needed?
    #
    ##########################################################################

    def sort_key_newest(self):
        return self.acq_reps + self.ret_reps

    ##########################################################################
    #
    # is_active
    #
    ##########################################################################

    def is_active(self):

        if self.active == False:
            return False
        
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
