#
# matplotlib_canvas.py <mike@peacecorps.org.cv>, <Peter.Bienstman@UGent.be>
#

from numpy import arange
from PyQt4 import QtGui

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from mnemosyne.libmnemosyne.translator import _


class MatplotlibCanvas(FigureCanvas):

    """A canvas to plot graphs according to the data and display contained in a
    model.

    """
    
    def __init__(self, parent, model, width=5, height=4):
        self.model = model
        colour = self._background_colour(parent)
        fig = Figure(figsize=(width, height), facecolor=colour,
                     edgecolor=colour)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.MinimumExpanding, 
                                   QtGui.QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        FigureCanvas.updateGeometry(self)

    def show_plot(self):
        if hasattr(self.model, "title"):
            self.axes.set_title(self.model.title)
        if hasattr(self.model, "xlabel"):
            self.axes.set_xlabel(self.model.xlabel)
        if hasattr(self.model, "ylabel"):
            self.axes.set_ylabel(self.model.ylabel)
        if not self.model.data:
            self.display_message(_("No stats available."))
            return
        functions = {"barchart": self.plot_barchart,
                     "histogram": self.plot_histogram,                     
                     "piechart": self.plot_piechart,
                     "linechart": self.plot_linechart}
        functions[self.model.plot_type]()

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
        self.model.extra_hints.setdefault("width", 1.0)
        self.model.extra_hints.setdefault("align", "center")
        if not hasattr(self.model, "xvalues"):
            self.model.xvalues = arange(len(self.model.data))
        if not hasattr(self.model, "xticks"):
            self.model.xticks = self.model.xvalues + 0.5
        if not hasattr(self.model, "xticklabels"):
            self.model.xticklabels = range(len(self.model.data))
        # Plot data.
        self.axes.bar(self.model.xvalues, self.model.data, **self.model.extra_hints)
        self.axes.set_xticks(self.model.xticks)
        self.axes.set_xticklabels(self.model.xticklabels)
        for label in self.axes.get_xticklabels():
            label.set_size("small")
        xmin, xmax = min(self.model.xvalues), max(self.model.xvalues)
        self.axes.set_xlim(xmin=xmin - 0.5, xmax=xmax + 0.5)
        max_value = max(self.model.data)
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
        if self.model.show_text_value == False:
            return
        non_zero = filter(bool, self.model.data)
        if non_zero:
            avg = lambda s: sum(s) / len(s)
            avg_height = avg(filter(bool, self.model.data))
        else:
            avg_height = 0
        pad = avg_height * 1.05 - avg_height
        for i in range(len(self.model.data)):
            height = self.model.data[i]
            if height == 0:
                continue
            self.axes.text(self.model.xvalues[i], height + pad, "%d" % height,
                           ha="center", va="bottom", fontsize="small")

    def plot_histogram(self):
        self.model.extra_hints.setdefault("align", "left")
        n, bins, patches = self.axes.hist(self.model.data,
                                          **self.model.extra_hints)
        xmin, xmax = self.model.extra_hints["range"]
        self.axes.set_xlim(xmin=xmin, xmax=xmax)
        self.axes.set_ylim(ymax=max(n)+1)

        def int_format(x, pos=None):
            if x == int(x):
                return "%d" % x
            else:
                return ""
        self.axes.yaxis.set_major_formatter(FuncFormatter(int_format))
        
    def plot_linechart(self):
        if not hasattr(self.model, "xvalues"):
            self.model.xvalues = arange(len(self.model.data))       
        self.axes.plot(self.model.xvalues, self.model.data, **self.model.extra_hints)
        
    def plot_piechart(self):
        # Pie charts look better on a square canvas, but the following does not
        # seem enough to achieve this, probably due to interplay with the Qt
        # layout manager. TODO: fix this.
        self.figure.set_size_inches(self.figure.get_figheight(),
                                    self.figure.get_figheight())
        self.axes.set_xlim(0.1, 0.8)
        self.axes.set_ylim(0.1, 0.8)
        # Only print percentage on wedges > 5%.
        self.model.extra_hints.setdefault("autopct",
            lambda x: "%1.1f%%" % x if x > 5 else "")
        self.axes.pie(self.model.data, **self.model.extra_hints)

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
