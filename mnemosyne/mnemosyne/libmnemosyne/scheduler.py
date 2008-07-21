##############################################################################
#
# scheduler.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# Scheduler
#
##############################################################################

class Scheduler(Plugin):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, name, description, can_be_unregistered=True):

        self.type                = "scheduler"
        self.name                = name
        self.description         = description
        self.can_be_unregistered = can_be_unregistered



    ##########################################################################
    #
    # Functions to be implemented by the actual scheduler.
    #
    ##########################################################################
        
    def calculate_initial_interval(grade):
        raise NotImplementedError

    def rebuild_revision_queue(learn_ahead = False):
        raise NotImplementedError

    def in_revision_queue(card):
        raise NotImplementedError
    
    def remove_from_revision_queue(card):
        raise NotImplementedError
    
    def get_new_question(learn_ahead = False):
        raise NotImplementedError
    
    def process_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError
