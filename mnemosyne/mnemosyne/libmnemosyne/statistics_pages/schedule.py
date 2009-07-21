#
# schedule.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Schedule(PlotStatisticsPage):

    name = _("Schedule")

    # TODO: add schedule for last week, last month and last year.
    
    NEXT_WEEK = 1
    NEXT_MONTH = 2
    NEXT_YEAR = 3

    variants = [(NEXT_WEEK, _("Next week")),
                (NEXT_MONTH, _("Next month")),
                (NEXT_YEAR, _("Next year"))]
    
    def prepare_statistics(self, variant):
        if variant == self.NEXT_WEEK:
            self.x = range(1, 8, 1)
        elif variant == self.NEXT_MONTH:   
            self.x = range(1, 32, 1)        
        elif variant == self.NEXT_YEAR:
            self.x = range(1, 366, 1)
        else:
            raise AttributeError, "Invalid variant"
        self.y = [self.scheduler().card_count_scheduled_between\
                  (day - 1, day) for day in self.x]
        
            
