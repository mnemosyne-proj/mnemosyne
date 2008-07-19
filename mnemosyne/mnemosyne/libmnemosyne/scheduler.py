##############################################################################
#
# scheduler.py <Peter.Bienstman@UGent.be>
#
##############################################################################

scheduler = []



##############################################################################
#
# Scheduler
#
##############################################################################

class Scheduler(object):

    def calculate_initial_interval(grade):
        raise NotImplementedError()

    def rebuild_revision_queue(learn_ahead = False):
        raise NotImplementedError()

    def in_revision_queue(card):
        raise NotImplementedError()
    
    def remove_from_revision_queue(card):
        raise NotImplementedError()
    
    def get_new_question(learn_ahead = False):
        raise NotImplementedError()
    
    def process_answer(self, card, new_grade, dry_run=False):
        raise NotImplementedError()


    
##############################################################################
#
# register_scheduler
#
#  Note: 'scheduler' is a list, the idea being that if the user unregisters
#  a custom scheduler, there is still the default scheduler which we can
#  access.
#
##############################################################################

def register_scheduler(scheduler_class):

    global scheduler

    scheduler.append(scheduler_class())



##############################################################################
#
# unregister_scheduler
#
##############################################################################

# TODO: test

def unregister_scheduler(scheduler_class):

    global scheduler

    for s in scheduler:
        if isinstance(s. scheduler_class):
            schedule.remove(s)
            break



##############################################################################
#
# get_scheduler
#
##############################################################################

def get_scheduler():

    return scheduler[-1]
