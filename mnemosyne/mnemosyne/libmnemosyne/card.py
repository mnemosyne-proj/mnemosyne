##############################################################################
#
# card.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import md5, time

from mnemosyne.libmnemosyne.component_manager import *



##############################################################################
#
# Card
#
#   Essentially the coming together of a Fact and a FactView.
#
##############################################################################

class Card(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, grade, fact, fact_view, id=None):

        self.fact = fact
        self.fact_view = fact_view

        self.reset_learning_data() # TODO: see where this is used and merge.

        # The initial grading is seen as the first repetition.

        # TODO: check if the way we do this now still treats imports
        # on equal footing.

        self.grade = grade
        self.acq_reps = 1
        self.acq_reps_since_lapse = 1

        db = get_database()
        self.last_rep = db.days_since_start()
        self.easiness = db.average_easiness()

        if id is not None:
            self.new_id()
        else:
            self.id = id

        sch = get_scheduler()

        new_interval  = sch.calculate_initial_interval(grade)
        new_interval += sch.calculate_interval_noise(new_interval)
        self.next_rep = db.days_since_start() + new_interval



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



# TODO: see which of these we still need and if they could be moved to
# database


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
    # is_new
    #
    ##########################################################################

    def is_new(self):
        return (self.acq_reps == 0) and (self.ret_reps == 0)


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
    # change_category
    #
    ##########################################################################

    def change_category(self, new_cat_name):

        old_cat = self.cat
        self.cat = get_category_by_name(new_cat_name)
        remove_category_if_unused(old_cat)
