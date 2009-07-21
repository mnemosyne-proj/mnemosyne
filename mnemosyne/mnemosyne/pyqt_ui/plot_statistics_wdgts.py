#
# plot_statistics_wdgts.py <mike@peacecorps.org.cv>, <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_pages.grades import Grades
from mnemosyne.libmnemosyne.statistics_pages.schedule import Schedule
from mnemosyne.libmnemosyne.statistics_pages.easiness import Easiness
from mnemosyne.libmnemosyne.ui_components.statistics_widget import StatisticsWidget


class PlotStatisticsWdgt(FigureCanvas, StatisticsWidget):

    """A canvas to plot graphs according to the data and display contained in a
    statistics page.

    """
    
    def __init__(self, parent, component_manager, page):
        StatisticsWidget.__init__(self, component_manager)
        self.page = page
        colour = self._background_colour(parent)
        fig = Figure(figsize=(5, 4), facecolor=colour, edgecolor=colour)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.MinimumExpanding, 
                                   QtGui.QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        FigureCanvas.updateGeometry(self)

    def display_message(self, text):
        self.axes.clear()
        self.axes.set_xticklabels("")
        self.axes.set_yticklabels("")
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, text, transform=self.axes.transAxes,
                       horizontalalignment="center", verticalalignment="center")

    def integers_only(self, x, pos=None):

        "Formatter to have only integer values on the axis."
        
        if x == int(x):
            return "%d" % x
        else:
            return ""
            
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
            return map(lambda x: x / 255.0, (r, g, b))


class ScheduleWdgt(PlotStatisticsWdgt):

    used_for = Schedule
    
    def show_statistics(self, variant):
        # Determine variant-dependent formatting.
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        ticklabels = lambda i, j, k: map(lambda x: "+%d" % x, range(i, j, k))        
        if variant == self.page.NEXT_WEEK:
            xticks = range(1, 8, 1)
            xticklabels = ticklabels(1, 8, 1)
            show_text_value = True
            linewidth = 1 
        elif variant == self.page.NEXT_MONTH:   
            xticks = [1] + range(5, 32, 5)
            xticklabels = ["+1"] + ticklabels(5, 32, 5)
            show_text_value = False
            linewidth = 1        
        elif variant == self.page.NEXT_YEAR:
            xticks = [1] + range(60, 365, 60)            
            xticklabels = ["+1"] + ticklabels(60, 365, 60)
            show_text_value = False
            linewidth = 0
        else:
            raise AttributeError, "Invalid variant"      
        # Plot data.
        self.axes.bar(self.page.x, self.page.y, width=1, align="center",
                      linewidth=linewidth, color="blue", alpha=0.75)
        self.axes.set_title(_("Number of cards scheduled"))
        self.axes.set_xlabel(_("Days")) 
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(xticklabels)
        xmin, xmax = min(self.page.x), max(self.page.x)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        self.axes.set_ylim(ymax=int(max(self.page.y) *  1.1) + 1)
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
        # Add exact numeric value above each bar. The text padding is based 
        # on the average height of non-zero bars. This gives a reasonable
        # padding for most data, but looks ugly when one bar is *much* larger
        # than the others. Note that bool() can be used as the filter function
        # since bool(0) == False.
        if show_text_value == False:
            return
        non_zero = filter(bool, self.page.y)
        if non_zero:
            avg = lambda s: sum(s) / len(s)
            avg_height = avg(filter(bool, self.page.y))
        else:
            avg_height = 0
        pad = avg_height * 1.05 - avg_height
        for i in range(len(self.page.y)):
            height = self.page.y[i]
            if height == 0:
                continue
            self.axes.text(self.page.x[i], height + pad, "%d" % height,
                           ha="center", va="bottom", fontsize="small")


class GradesWdgt(PlotStatisticsWdgt):

    used_for = Grades
    
    def show_statistics(self, variant):
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        self.axes.bar(self.page.x, self.page.y, width=0.7, align="center",
            color="green", alpha=0.75)
        self.axes.set_title(_("Number of cards"))
        self.axes.set_xlabel(_("Grades"))
        self.axes.set_xticks(self.page.x)
        self.axes.set_xticklabels([_("Not seen")] + range(0, 6))
        for label in self.axes.get_xticklabels():
            label.set_size("small")
        xmin, xmax = min(self.page.x), max(self.page.x)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        self.axes.set_ylim(ymax=int(max(self.page.y) *  1.1) + 1)
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
        for label in self.axes.get_yticklabels():
            label.set_size("small")


class EasinessWdgt(PlotStatisticsWdgt):

    used_for = Easiness
    
    def show_statistics(self, variant):
        if not self.page.data:
            self.display_message(_("No stats available."))
            return
        n, bins, patches = self.axes.hist(self.page.data, range=(1.3, 3.7),
            bins=24, align="left", facecolor="red", alpha=0.75)
        self.axes.set_title(_("Number of cards"))
        self.axes.set_xlabel(_("Easiness"))
        self.axes.set_xlim(xmin=1.3, xmax=3.7)
        self.axes.set_ylim(ymax=int(max(n) *  1.1) + 1)
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.integers_only))
