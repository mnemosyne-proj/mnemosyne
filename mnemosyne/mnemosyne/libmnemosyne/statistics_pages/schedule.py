#
# schedule.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Schedule(PlotStatisticsPage):

    name = _("Schedule")
    
    NEXT_WEEK = 1
    NEXT_MONTH = 2
    NEXT_YEAR = 3
    LAST_WEEK = 4
    LAST_MONTH = 5
    LAST_YEAR = 6

    variants = [(NEXT_WEEK, _("Next week")),
                (NEXT_MONTH, _("Next month")),
                (NEXT_YEAR, _("Next year")),
                (LAST_WEEK, _("Last week")),
                (LAST_MONTH, _("Last month")),
                (LAST_YEAR, _("Last year"))]
    
    def prepare_statistics(self, variant):
        if variant == self.NEXT_WEEK:
            self.x = range(1, 8, 1)
        elif variant == self.NEXT_MONTH:   
            self.x = range(1, 32, 1)        
        elif variant == self.NEXT_YEAR:
            self.x = range(1, 366, 1)
        elif variant == self.LAST_WEEK:
            self.x = range(-7, 1, 1)
        elif variant == self.LAST_MONTH:
            self.x = range(-31, 1, 1)
        elif variant == self.LAST_YEAR:
            self.x = range(-365, 1, 1)
        else:
            raise AttributeError, "Invalid variant"
        self.y = [self.scheduler().card_count_scheduled_n_days_from_now(n=day)
                  for day in self.x]
        
            
