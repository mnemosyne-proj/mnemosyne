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
#   TODO: make sure we cache days_since_start where possible to save time.
#
##############################################################################

class StartDate:
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, start=None):
        
        self.init(start)


            
    ##########################################################################
    #
    # init
    #
    ##########################################################################

    def init(self, start=None):

        if not start:
            self.start = datetime.datetime.now()
        else:
            self.start = start


            
    ##########################################################################
    #
    # days_since_start
    #
    ##########################################################################
    
    def days_since_start(self):
        
        h = config["day_starts_at"]

        adjusted_start = self.start.replace(hour=h, minute=0, second=0)
        
        dt = datetime.datetime.now() - adjusted_start
                
        return dt.days



##############################################################################
#
# The start date needs to be accessed by many different parts of the
# library, so we hold it in a global variable.
#
##############################################################################

start_date = StartDate()
