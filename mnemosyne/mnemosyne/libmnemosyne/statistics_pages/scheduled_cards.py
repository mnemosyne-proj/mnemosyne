#
# cards_scheduled.py <Peter.Bienstman@UGent.be>, <mike@peacecorps.org.cv>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage

DAY = 24 * 60 * 60 # Seconds in a day.


class ScheduledCards(StatisticsPage):

    name = _("Schedule")

    # TODO: add schedule for last week, last month and last year.
    
    NEXT_WEEK = 1
    NEXT_MONTH = 2
    NEXT_YEAR = 3

    variants = [(NEXT_WEEK, _("Next week")),
                (NEXT_MONTH, _("Next month")),
                (NEXT_YEAR, _("Next year"))]
    
    def prepare(self, variant):               
        self.plot_type = "barchart"
        self.title = _("Number of cards scheduled")
        self.xlabel = _("Days") 
        xticklabels = lambda i, j, k: map(lambda x: "+%d" % x, range(i, j, k))        
        if variant == self.NEXT_WEEK:
            self.xvalues = range(1, 8, 1)
            self.xticks = range(1, 8, 1)
            self.xticklabels = xticklabels(1, 8, 1)
            self.show_text_value = True
        elif variant == self.NEXT_MONTH:   
            self.xvalues = range(1, 32, 1)
            self.xticks = [1] + range(5, 32, 5)
            self.xticklabels = ["+1"] + xticklabels(5, 32, 5)
            self.show_text_value = True          
        elif variant == self.NEXT_YEAR:
            self.xvalues = range(1, 366, 1)
            self.xticks = [1] + range(60, 365, 60)            
            self.xticklabels = ["+1"] + xticklabels(60, 365, 60)
            self.show_text_value = False
            self.extra_hints["linewidth"] = 0
        else:
            raise ArgumentError, "Invalid variant for CardsScheduled"
        self.data = []
        now = self.scheduler().adjusted_now()
        for day in self.xvalues:
            self.data.append(self.database().con.execute(\
                """select count() from cards where active=1 and grade>=2
                and ?<next_rep and next_rep<=?""",
                (now + (day - 1) * DAY, now + day * DAY)).fetchone()[0])
            
