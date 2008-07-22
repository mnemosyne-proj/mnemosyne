##############################################################################
#
# start_date.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import datetime
from mnemosyne.libmnemosyne.config import config



##############################################################################
#
# StartDate
#
#   The days_since_start information is frequently needed, so rather than
#   calculating it each time, we store it in a class variable, which we
#   need to update when the database loads and in rebuild_revision_queue. 
#
##############################################################################

class StartDate:

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, start=None):

        h = config["day_starts_at"]

        if not start:
            start = datetime.datetime.now()
        
        t = time.localtime(start_time)
        
        time = time.mktime([t[0],t[1],t[2], h,0,0, t[6],t[7],t[8]])

        self.start = datetime.datetime.fromtimestamp(time)

        self.update_days_since_start()


            
    ##########################################################################
    #
    # update_days_since_start
    #
    ##########################################################################
    
    def update_days_since_start(self):
        
        h = config["day_starts_at"]
        
        adjusted_now = datetime.datetime.now() - datetime.timedelta(hours=h)
        dt = adjusted_now.date() - self.start.date()
        
        self.days_since_start = dt.days




start_date = None

def initialise_start_date(start):
    
    global start_date
    start_date = StartDate()   
