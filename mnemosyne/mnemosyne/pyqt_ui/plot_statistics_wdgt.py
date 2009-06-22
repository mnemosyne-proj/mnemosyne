#
# matplotlib_canvas.py <mike@peacecorps.org.cv>, <Peter.Bienstman@UGent.be>
#

from numpy import arange
from PyQt4 import QtGui

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage
from mnemosyne.libmnemosyne.ui_components.statistics_widget import StatisticsWidget


class PlotStatisticsWdgt(FigureCanvas, StatisticsWidget):

    """A canvas to plot graphs according to the data and display contained in a
    statistics page.

    """

    used_for = PlotStatisticsPage
    
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

    def show_statistics(self):
        if hasattr(self.page, "title"):
            self.axes.set_title(self.page.title)
        if hasattr(self.page, "xlabel"):
            self.axes.set_xlabel(self.page.xlabel)
        if hasattr(self.page, "ylabel"):
            self.axes.set_ylabel(self.page.ylabel)
        if not self.page.data:
            self.display_message(_("No stats available."))
            return
        functions = {"barchart": self.plot_barchart,
                     "histogram": self.plot_histogram,                     
                     "piechart": self.plot_piechart,
                     "linechart": self.plot_linechart}
        functions[self.page.plot_type]()

    def display_message(self, text):
        self.axes.clear()
        self.axes.set_xticklabels("")
        self.axes.set_yticklabels("")
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, text, transform=self.axes.transAxes,
                       horizontalalignment="center", verticalalignment="center")

    def plot_barchart(self):
        # Set default parameters.
        self.page.extra_hints.setdefault("width", 1.0)
        self.page.extra_hints.setdefault("align", "center")
        if not hasattr(self.page, "xvalues"):
            self.page.xvalues = arange(len(self.page.data))
        if not hasattr(self.page, "xticks"):
            self.page.xticks = self.page.xvalues + 0.5
        if not hasattr(self.page, "xticklabels"):
            self.page.xticklabels = range(len(self.page.data))
        # Plot data.
        self.axes.bar(self.page.xvalues, self.page.data, **self.page.extra_hints)
        self.axes.set_xticks(self.page.xticks)
        self.axes.set_xticklabels(self.page.xticklabels)
        for label in self.axes.get_xticklabels():
            label.set_size("small")
        xmin, xmax = min(self.page.xvalues), max(self.page.xvalues)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        max_value = max(self.page.data)
        tick_interval = round((max_value / 4.0) + 1)
        self.axes.set_yticks(arange(tick_interval, max_value + tick_interval, 
                                    tick_interval))
        self.axes.set_ylim(ymax=max_value + 0.5 * tick_interval)
        for label in self.axes.get_yticklabels():
            label.set_size("small")
        # Add exact numeric value above each bar. The text padding is based 
        # on the average height of non-zero bars. This gives a reasonable
        # padding for most data, but looks ugly when one bar is *much* larger
        # than the others. Note that bool() can be used as the filter function
        # since bool(0) == False.
        if self.page.show_text_value == False:
            return
        non_zero = filter(bool, self.page.data)
        if non_zero:
            avg = lambda s: sum(s) / len(s)
            avg_height = avg(filter(bool, self.page.data))
        else:
            avg_height = 0
        pad = avg_height * 1.05 - avg_height
        for i in range(len(self.page.data)):
            height = self.page.data[i]
            if height == 0:
                continue
            self.axes.text(self.page.xvalues[i], height + pad, "%d" % height,
                           ha="center", va="bottom", fontsize="small")

    def plot_histogram(self):
        self.page.extra_hints.setdefault("align", "left")
        n, bins, patches = self.axes.hist(self.page.data,
                                          **self.page.extra_hints)
        xmin, xmax = self.page.extra_hints["range"]
        self.axes.set_xlim(xmin=xmin, xmax=xmax)
        self.axes.set_ylim(ymax=max(n)+1)

        def int_format(x, pos=None):
            if x == int(x):
                return "%d" % x
            else:
                return ""
        self.axes.yaxis.set_major_formatter(FuncFormatter(int_format))
        
    def plot_linechart(self):
        if not hasattr(self.page, "xvalues"):
            self.page.xvalues = arange(len(self.page.data))       
        self.axes.plot(self.page.xvalues, self.page.data, **self.page.extra_hints)
        
    def plot_piechart(self):
        # Pie charts look better on a square canvas, but the following does not
        # seem enough to achieve this, probably due to interplay with the Qt
        # layout manager. TODO: fix this.
        self.figure.set_size_inches(self.figure.get_figheight(),
                                    self.figure.get_figheight())
        self.axes.set_xlim(0.1, 0.8)
        self.axes.set_ylim(0.1, 0.8)
        # Only print percentage on wedges > 5%.
        self.page.extra_hints.setdefault("autopct",
            lambda x: "%1.1f%%" % x if x > 5 else "")
        self.axes.pie(self.page.data, **self.page.extra_hints)

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
