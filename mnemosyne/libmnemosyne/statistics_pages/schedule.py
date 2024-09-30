#
# schedule.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage


class Schedule(PlotStatisticsPage):

    name = _("Schedule")

    NEXT_WEEK = 1
    NEXT_MONTH = 2
    NEXT_3_MONTHS = 3
    NEXT_6_MONTHS = 4
    NEXT_YEAR = 5
    LAST_WEEK = 6
    LAST_MONTH = 7
    LAST_3_MONTHS = 8
    LAST_6_MONTHS = 9
    LAST_YEAR = 10

    variants = [(NEXT_WEEK, _("Next week (active cards only)")),
                (NEXT_MONTH, _("Next month (active cards only)")),
                (NEXT_3_MONTHS, _("Next 3 months (active cards only)")),
                (NEXT_6_MONTHS, _("Next 6 months (active cards only)")),
                (NEXT_YEAR, _("Next year (active cards only)")),
                (LAST_WEEK, _("Last week (all cards)")),
                (LAST_MONTH, _("Last month (all cards)")),
                (LAST_3_MONTHS, _("Last 3 months (all cards)")),
                (LAST_6_MONTHS, _("Last 6 months (all cards)")),
                (LAST_YEAR, _("Last year (all cards)"))]

    def prepare_statistics(self, variant):
        if variant == self.NEXT_WEEK:
            self.x = list(range(1, 8, 1))
        elif variant == self.NEXT_MONTH:
            self.x = list(range(1, 32, 1))
        elif variant == self.NEXT_3_MONTHS:
            self.x = list(range(1, 92, 1))
        elif variant == self.NEXT_6_MONTHS:
            self.x = list(range(1, 183, 1))
        elif variant == self.NEXT_YEAR:
            self.x = list(range(1, 366, 1))
        elif variant == self.LAST_WEEK:
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
            self.y.append(\
                self.scheduler().card_count_scheduled_n_days_from_now(n=day))
            self.main_widget().increase_progress(1)
        self.main_widget().close_progress()

