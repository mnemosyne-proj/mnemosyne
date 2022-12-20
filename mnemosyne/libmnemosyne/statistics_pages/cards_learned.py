#
# cards_learned.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class CardsLearned(PlotStatisticsPage):

    name = _("Cards learned")

    LAST_WEEK = 1
    LAST_MONTH = 2
    LAST_3_MONTHS = 3
    LAST_6_MONTHS = 4
    LAST_YEAR = 5

    variants = [(LAST_WEEK, _("Last week")),
                (LAST_MONTH, _("Last month")),
                (LAST_3_MONTHS, _("Last 3 months")),
                (LAST_6_MONTHS, _("Last 6 months")),
                (LAST_YEAR, _("Last year"))]

    def prepare_statistics(self, variant):
        if variant == self.LAST_WEEK:
            self.x = list(range(-7, 1, 1))
        elif variant == self.LAST_MONTH:
            self.x = list(range(-31, 1, 1))
        elif variant == self.LAST_3_MONTHS:
            self.x = list(range(-91, 1, 1))
        elif variant == self.LAST_6_MONTHS:
            self.x = list(range(-182, 1, 1))
        elif variant == self.LAST_YEAR:
            self.x = list(range(-365, 1, 1))
        else:
            raise AttributeError("Invalid variant")
        self.main_widget().set_progress_text(_("Calculating statistics..."))
        self.main_widget().set_progress_range(len(self.x))
        self.main_widget().set_progress_update_interval(3)
        self.y = []
        for day in self.x:
            self.y.append(self.database().card_count_learned_n_days_ago(n=-day))
            self.main_widget().increase_progress(1)
        self.main_widget().close_progress()



