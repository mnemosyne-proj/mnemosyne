#
# cards_scheduled.py <Peter.Bienstman@UGent.be>, <mike@peacecorps.org.cv>,
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


class CardsScheduled(StatisticsPage):

    name = _("Schedule")
    
    NEXT_WEEK = 1
    NEXT_MONTH = 2
    NEXT_YEAR = 3

    scopes = [(NEXT_WEEK, _("Next week")),
              (NEXT_MONTH, _("Next month")),
              (NEXT_YEAR, _("Next year"))]
    
    def prepare(self, scope):
        self.plot_type = "barchart" # TODO: linechart for year scope?
        xticklabels = lambda i, j: map(lambda x: "+%d" % x, range(i, j))        
        if self.scope == self.NEXT_WEEK:
            _range = range(0, 7, 1)
            self.xlabel = _("Days") 
            self.xticklabels = [_("Today")] + xticklabels(1, 7)
        elif self.scope == self.NEXT_MONTH: 
            _range = range(6, 28, 7)
            self.xlabel = _("Weeks")
            self.xticklabels = ["This week"] + xticklabels(1, 4)           
        elif self.scope == self.NEXT_YEAR:
            _range = range(30, 365, 30)
            self.xlabel = _("Months")
            self.xticklabels = xticklabels(0, 12)            
        else:
            raise ArgumentError, "Invalid scope for CardsScheduled"
        self.ylabel = _("Number of cards scheduled")
        
        # TMP:
        # TODO: reorder data and presentation hint code.
        import scipy
        self.data = scipy.random.randint(0, 200, (len(range_),))
        return
        
        old_cumulative = 0
        self.data = []
        for days in range_:
            cumulative = self.database().scheduled_count(days)
            self.data.append(cumulative - old_cumulative)
            old_cumulative = cumulative
            
