
##############################################################################
#
# start_date.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import time, datetime
from mnemosyne.libmnemosyne.config import get_config



##############################################################################
#
# StartTime
#
# TODO: remove obsolete code?
#
##############################################################################

time_of_start = None

class StartTime:

    def __init__(self, start_time):
        
        h = get_config("day_starts_at")

        # Compatibility code for older versions.
        
        t = time.localtime(start_time) # In seconds from Unix epoch in UTC.
        self.time = time.mktime([t[0],t[1],t[2], h,0,0, t[6],t[7],t[8]])

        # New implementation.

        self.date = datetime.datetime.fromtimestamp(self.time).date()

    # Since this information is frequently needed, we calculate it once
    # and store it in a global variable, which is updated when the database
    # loads and in rebuild_revision_queue.
    
    def update_days_since(self):
        
        global days_since_start

        # If this is a database with the obsolete time stamp, update it
        # with a date attribute. The adjustment for 'day_starts_at' is not
        # relevant here, as we only store the date part.
        
        if not getattr(self, 'date', None):
            self.date = datetime.datetime.fromtimestamp(self.time).date()
        
        # Now calculate the difference in days.
        
        h = get_config("day_starts_at")
        adjusted_now = datetime.datetime.now() - datetime.timedelta(hours=h)
        dt = adjusted_now.date() - self.date
        
        days_since_start = dt.days



##############################################################################
#
# initialise_time_of_start
#
##############################################################################

def initialise_time_of_start():

    global time_of_start

    time_of_start = StartTime(time.time())
    time_of_start.update_days_since()



##############################################################################
#
# get_days_since_start
#
# TODO: profile speed of this function, as it's critical
# Is an exposed global faster/possible ?
#
##############################################################################

days_since_start = None

def get_days_since_start():
    return days_since_start
