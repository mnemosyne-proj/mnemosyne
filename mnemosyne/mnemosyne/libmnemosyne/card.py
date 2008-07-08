##############################################################################
#
# card.py <Peter.Bienstman@UGent.be>
#
##############################################################################



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

cards = []

class Card:

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.id = 0

        self.card_type = None

        self.fact = None

        self.subcard = 0

        self.date_added = None # TODO
        
        self.q   = None
        self.a   = None
        self.cat = []
        
        self.reset_learning_data()

    ##########################################################################
    #
    # filtered_q
    #
    ##########################################################################

    def filtered_q(): # TODO: update

        # q = self.card_type.generate_q(self.fact, self.subcard)
        # q = preprocess(q)

        return q

    ##########################################################################
    #
    # filtered_a
    #
    ##########################################################################
    
    def filtered_a(): # TODO: update

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
        return (self.grade < 2) and (self.cat.active == True)
    
    ##########################################################################
    #
    # is_due_for_retention_rep
    #
    #  Due for a retention repetion within 'days' days?
    #
    ##########################################################################
    
    def is_due_for_retention_rep(self, days=0):
        return (self.grade >= 2) and (self.cat.active == True) and \
               (days_since_start >= self.next_rep - days)

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
    # is_in_active_category
    #
    ##########################################################################

    def is_in_active_category(self):
        return (self.cat.active == True)

    ##########################################################################
    #
    # qualifies_for_learn_ahead
    #
    ##########################################################################
    
    def qualifies_for_learn_ahead(self):
        return (self.grade >= 2) and (self.cat.active == True) and \
               (days_since_start < self.next_rep) 
        
    ##########################################################################
    #
    # change_category
    #
    ##########################################################################
    
    def change_category(self, new_cat_name):

        old_cat = self.cat
        self.cat = get_category_by_name(new_cat_name)
        remove_category_if_unused(old_cat)



##############################################################################
#
# cards_are_inverses
#
##############################################################################

def cards_are_inverses(card1, card2):

    if card1.q == card2.a and card2.q == card1.a:
        return True
    else:
        return False



##############################################################################
#
# get_cards
#
##############################################################################

def get_cards():
    return cards



##############################################################################
#
# get_card_by_id
#
##############################################################################

def get_card_by_id(id):
    try:
        return [i for i in cards if i.id == id][0]
    except:
        return None



##############################################################################
#
# number_of_cards
#
##############################################################################

def number_of_cards():
    return len(cards)



##############################################################################
#
# non_memorised_cards
#
##############################################################################

def non_memorised_cards():
    return sum(1 for i in cards if i.is_due_for_acquisition_rep())



##############################################################################
#
# scheduled_cards
#
#   Number of cards scheduled within 'days' days.
#
##############################################################################

def scheduled_cards(days=0):
    return sum(1 for i in cards if i.is_due_for_retention_rep(days))



##############################################################################
#
# active_cards
#
#   Number of cards in an active category.
#
##############################################################################

def active_cards():
    return sum(1 for i in cards if i.is_in_active_category())



##############################################################################
#
# average_easiness
#
##############################################################################

def average_easiness():

    if len(cards) == 0:
        return 2.5
    if len(cards) == 1:
        return cards[0].easiness
    else:
        return sum(i.easiness for i in cards) / len(cards)
