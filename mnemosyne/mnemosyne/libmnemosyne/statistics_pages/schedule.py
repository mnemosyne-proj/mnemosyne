#
# schedule.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage

DAY = 24 * 60 * 60 # Seconds in a day.


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
        now = self.scheduler().adjusted_now()
        self.y = [] # Don't forget to reset this after variant change.
        for day in self.x:
            self.y.append(self.database().card_count_scheduled_between\
                (now + (day - 1) * DAY, now + day * DAY))
            
