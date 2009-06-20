#
# easiness.py <Peter.Bienstman@UGent.be>, <mike@peacecorps.org.cv>,
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


class Easiness(StatisticsPage):

    name = _("Easiness")
    
    ALL_CARDS = 0

    variants = [(ALL_CARDS, _("All cards"))]
        
    def prepare(self, variant):                
        self.plot_type = "histogram"
        self.title = _("Number of cards")
        self.xlabel = _("Easiness")
        if variant == self.ALL_CARDS:
            self.data = [cursor[0] for cursor in self.database().con.execute(\
            """select easiness from cards where active=1 and grade>=2""")]

