#
# avg_grade_statistics.py <Peter.Bienstman@gmail.com>
#

from openSM2sync.log_entry import EventTypes
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage
from mnemosyne.pyqt_ui.statistics_wdgts_plotting import BarChartDaysWdgt

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


# The average grade statistics page (GUI independent part).

class AvgGrade(PlotStatisticsPage):

    name = "Average grades"

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

    def avg_grade_n_days_ago(self, n):
        start_of_day = self.database().start_of_day_n_days_ago(n)
        return self.database().con.execute(\
            """select avg(grade) from log where ?<=timestamp and timestamp<?
            and event_type=? and scheduled_interval!=0""",
            (start_of_day, start_of_day + DAY, EventTypes.REPETITION)).\
            fetchone()[0]

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
        self.y = [self.avg_grade_n_days_ago(n=-day) for day in self.x]


# The custom widget.

class AvgGradeWdgt(BarChartDaysWdgt):

    title = _("Average grades of scheduled cards")
    used_for = AvgGrade

    def show_statistics(self, variant):
        self.activate()
        # Determine variant-dependent formatting.
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        ticklabels_neg = lambda i, j, k: ["%d" % x for x in range(i, j, k)]
        if hasattr(self.page, "LAST_WEEK") and \
            variant == self.page.LAST_WEEK:
            xticks = list(range(-7, 1, 1))
            xticklabels = ticklabels_neg(-7, 1, 1)
        elif hasattr(self.page, "LAST_MONTH") and \
            variant == self.page.LAST_MONTH:
            xticks = list(range(-30, -4, 5)) + [0]
            xticklabels = ticklabels_neg(-30, -4, 5) + ["0"]

        elif hasattr(self.page, "LAST_3_MONTHS") and \
            variant == self.page.LAST_3_MONTHS:
            xticks = list(range(-90, -9, 10)) + [0]
            xticklabels = ticklabels_neg(-90, -9, 10) + ["0"]

        elif hasattr(self.page, "LAST_6_MONTHS") and \
            variant == self.page.LAST_6_MONTHS:
            xticks = list(range(-180, -19, 20)) + [0]
            xticklabels = ticklabels_neg(-180, -19, 20) + ["0"]
        elif hasattr(self.page, "LAST_YEAR") and \
            variant == self.page.LAST_YEAR:
            xticks = list(range(-360, -59, 60)) + [0]
            xticklabels = ticklabels_neg(-360, -59, 60) + ["0"]
        else:
            raise AttributeError("Invalid variant")
        # Plot data.
        self.axes.plot(self.page.x, self.page.y)
        self.axes.set_title(self.title)
        self.axes.set_xlabel(_("Days"))
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels)
        xmin, xmax = min(self.page.x), max(self.page.x)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)

# Wrap it into a Plugin and then register the Plugin.

class AvgGradePlugin(Plugin):
    name = "Average grades"
    description = "Average grade given to scheduled cards as a function of time"
    components = [AvgGrade, AvgGradeWdgt]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(AvgGradePlugin)

