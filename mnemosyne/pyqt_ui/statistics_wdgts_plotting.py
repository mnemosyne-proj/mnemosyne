#
# statistics_wdgts_plotting.py <mike@peacecorps.org.cv>, <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.statistics_pages.grades import Grades
from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
from mnemosyne.libmnemosyne.statistics_pages.easiness import Easiness
from mnemosyne.libmnemosyne.statistics_pages.cards_added import CardsAdded
from mnemosyne.libmnemosyne.statistics_pages.cards_learned import CardsLearned
from mnemosyne.libmnemosyne.statistics_pages.retention_score import RetentionScore
from mnemosyne.libmnemosyne.ui_components.statistics_widget import StatisticsWidget


class PlotStatisticsWdgt(QtWidgets.QWidget, StatisticsWidget):

    """A canvas to plot graphs according to the data and display contained in a
    statistics page.

    """

    def __init__(self, parent, page, **kwds):
        super().__init__(**kwds)
        self.parent = parent
        self.page = page

    def activate(self):
        StatisticsWidget.activate(self)

        # Late import to speed up app startup.
        import warnings
        warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*",
                                category=UserWarning)
        from matplotlib import rcParams
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_qtagg import FigureCanvas

        self.setMinimumSize(640, 480)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                           QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        colour = self._background_colour(self.parent)
        fig = Figure(facecolor=colour, edgecolor=colour)
        self.canvas = FigureCanvas(fig)
        self.vbox_layout = QtWidgets.QVBoxLayout(self)
        self.vbox_layout.addWidget(self.canvas)
        self.canvas.setMinimumSize(640, 480)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                  QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.canvas.setParent(self)
        self.axes = fig.add_subplot(111)
        self.canvas.updateGeometry()
        if self.config()["ui_language"].lower().startswith("zh"):
            rcParams['font.sans-serif'] = \
                ["Microsoft YaHei", "WenQuanYi Zen Hei", "Ume P Gothic O5"]

    def display_message(self, text):
        self.axes.clear()
        self.axes.set_xticklabels("")
        self.axes.set_yticklabels("")
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, text, transform=self.axes.transAxes,
                       horizontalalignment="center", verticalalignment="center")

    def integers_only(self, x, pos=None):

        """Formatter to have only integer values on the axis."""

        if x == int(x):
            return "%d" % x
        else:
            return ""

    def _add_numbers_to_bars(self):
        # Add exact numeric value above each bar. The text padding is based
        # on the average height of non-zero bars. This gives a reasonable
        # padding for most data, but looks ugly when one bar is *much* larger
        # than the others. Note that bool() can be used as the filter function
        # since bool(0) == False.
        non_zero = list(filter(bool, self.page.y))
        if non_zero:
            avg = lambda s: sum(s) / len(s)
            avg_height = avg(list(filter(bool, self.page.y)))
        else:
            avg_height = 0
        pad = avg_height * 1.05 - avg_height
        for i in range(len(self.page.y)):
            height = self.page.y[i]
            if height == 0:
                continue
            self.axes.text(self.page.x[i], height + pad, "%d" % height,
                           ha="center", va="bottom", fontsize="small")

    def _background_colour(self, parent):

        """Return the parent's background colour.

        Sadly, this won't work on OS X, XP, or Vista since they use native
        theme engines for drawing, rather than the palette. See:
        http://doc.trolltech.com/4.4/qapplication.html#setPalette

        """

        if parent.style().objectName() == "macintosh (Aqua)":
            return "0.91"
        else:
            r, g, b, a = parent.palette().color(parent.backgroundRole()).getRgb()
            return [x / 255.0 for x in (r, g, b)]


class BarChartDaysWdgt(PlotStatisticsWdgt):

    colour = "blue"

    def show_statistics(self, variant):
        self.activate()
        # Determine variant-dependent formatting.
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        ticklabels_pos = lambda i, j, k: ["+%d" % x for x in range(i, j, k)]
        ticklabels_neg = lambda i, j, k: ["%d" % x for x in range(i, j, k)]
        if hasattr(self.page, "NEXT_WEEK") and \
               variant == self.page.NEXT_WEEK:
            xticks = list(range(1, 8, 1))
            xticklabels = ticklabels_pos(1, 8, 1)
            show_text_value = True
            linewidth = 1
        elif hasattr(self.page, "NEXT_MONTH") and \
            variant == self.page.NEXT_MONTH:
            xticks = [1] + list(range(5, 32, 5))
            xticklabels = ["+1"] + ticklabels_pos(5, 32, 5)
            show_text_value = False
            linewidth = 1
        elif hasattr(self.page, "NEXT_3_MONTHS") and \
            variant == self.page.NEXT_3_MONTHS:
            xticks = [1] + list(range(10, 92, 10))
            xticklabels = ["+1"] + ticklabels_pos(10, 92, 10)
            show_text_value = False
            linewidth = 1
        elif hasattr(self.page, "NEXT_6_MONTHS") and \
            variant == self.page.NEXT_6_MONTHS:
            xticks = [1] + list(range(30, 183, 30))
            xticklabels = ["+1"] + ticklabels_pos(30, 183, 30)
            show_text_value = False
            linewidth = 0
        elif hasattr(self.page, "NEXT_YEAR") and \
                 variant == self.page.NEXT_YEAR:
            xticks = [1] + list(range(60, 365, 60))
            xticklabels = ["+1"] + ticklabels_pos(60, 365, 60)
            show_text_value = False
            linewidth = 0
        elif hasattr(self.page, "LAST_WEEK") and \
            variant == self.page.LAST_WEEK:
            xticks = list(range(-7, 1, 1))
            xticklabels = ticklabels_neg(-7, 1, 1)
            show_text_value = True
            linewidth = 1
        elif hasattr(self.page, "LAST_MONTH") and \
            variant == self.page.LAST_MONTH:
            xticks = list(range(-30, -4, 5)) + [0]
            xticklabels = ticklabels_neg(-30, -4, 5) + ["0"]
            show_text_value = False
            linewidth = 1
        elif hasattr(self.page, "LAST_3_MONTHS") and \
            variant == self.page.LAST_3_MONTHS:
            xticks = list(range(-90, -9, 10)) + [0]
            xticklabels = ticklabels_neg(-90, -9, 10) + ["0"]
            show_text_value = False
            linewidth = 1
        elif hasattr(self.page, "LAST_6_MONTHS") and \
            variant == self.page.LAST_6_MONTHS:
            xticks = list(range(-180, -19, 20)) + [0]
            xticklabels = ticklabels_neg(-180, -19, 20) + ["0"]
            show_text_value = False
            linewidth = 0
        elif hasattr(self.page, "LAST_YEAR") and \
            variant == self.page.LAST_YEAR:
            xticks = list(range(-360, -59, 60)) + [0]
            xticklabels = ticklabels_neg(-360, -59, 60) + ["0"]
            show_text_value = False
            linewidth = 0
        else:
            raise AttributeError("Invalid variant")
        # Plot data.
        self.axes.bar(self.page.x, self.page.y, width=1, align="center",
                      linewidth=linewidth, color=self.colour, alpha=0.75,
                      edgecolor="black")
        self.axes.set_title(self.title)
        self.axes.set_xlabel(_("Days"))
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels)
        xmin, xmax = min(self.page.x), max(self.page.x)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        # Quick and dirty fix to have retention plot always max out at 100%,
        # except for LAST_WEEK, when we need space to put the numbers.
        if variant == self.page.LAST_WEEK or not hasattr(self, "y_max"):
            self.axes.set_ylim(ymax=int(max(self.page.y) *  1.1) + 1)
        else:
            self.axes.set_ylim(ymax=self.y_max)
        from matplotlib.ticker import FuncFormatter
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
        if show_text_value:
            self._add_numbers_to_bars()


class ScheduleWdgt(BarChartDaysWdgt):

    title = _("Number of cards scheduled")
    used_for = Schedule

    def activate(self):
        super().activate()
        self.title = _(self.title)


class RetentionScoreWdgt(BarChartDaysWdgt):

    used_for = RetentionScore
    colour = "green"
    title = _("Retention score (%)")
    y_max = 100

    def activate(self):
        super().activate()
        self.title = _(self.title)


class CardsAddedWdgt(BarChartDaysWdgt):

    used_for = CardsAdded
    colour = "red"
    title = _("Number of cards added")

    def activate(self):
        super().activate()
        self.title = _(self.title)


class CardsLearnedWdgt(BarChartDaysWdgt):

    used_for = CardsLearned
    colour = "yellow"
    title = _("Number of new cards learned")

    def activate(self):
        super().activate()
        self.title = _(self.title)


class GradesWdgt(PlotStatisticsWdgt):

    used_for = Grades

    def show_statistics(self, variant):
        self.activate()
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        self.axes.bar(self.page.x, self.page.y, width=0.7, align="center",
            linewidth=1, edgecolor="black", color="blue", alpha=0.75)
        self.axes.set_title(_("Number of cards"))
        self.axes.set_xlabel(_("Grades"))
        self.axes.set_xticks(self.page.x)
        self.axes.set_xticklabels([_("Not seen")] + list(range(0, 6)))
        xmin, xmax = min(self.page.x), max(self.page.x)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        self.axes.set_ylim(ymax=int(max(self.page.y) *  1.1) + 1)
        from matplotlib.ticker import FuncFormatter
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
        self._add_numbers_to_bars()


class EasinessWdgt(PlotStatisticsWdgt):

    used_for = Easiness

    def show_statistics(self, variant):
        self.activate()
        if not self.page.data:
            self.display_message(_("No stats available."))
            return
        n, bins, patches = self.axes.hist(self.page.data, range=(1.3, 3.7),
            bins=24, align="left", facecolor="red", alpha=0.75, 
            linewidth=1, edgecolor="black")
        self.axes.set_title(_("Number of cards"))
        self.axes.set_xlabel(_("Easiness"))
        self.axes.set_xlim(xmin=1.3, xmax=3.7)
        self.axes.set_ylim(ymax=int(max(n) *  1.1) + 1)
        from matplotlib.ticker import FuncFormatter
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
