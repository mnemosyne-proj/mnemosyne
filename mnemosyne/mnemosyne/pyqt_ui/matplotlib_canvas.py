#
# matplotlib_canvas.py <mike@peacecorps.org.cv>, <Peter.Bienstman@UGent.be>
#

from numpy import arange
from PyQt4 import QtGui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibCanvas(FigureCanvas):
    
    def __init__(self, parent, width=5, height=4):
        colour = self._background_colour(parent)
        fig = Figure(figsize=(width, height), facecolor=colour,
                     edgecolor=colour)
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

    def plot_bargraph(self, values, **kwargs):
        kwargs.setdefault("width", 1.0)
        kwargs.setdefault("align", "center")
        kwargs.setdefault("alpha", 0.7)
        kwargs.setdefault("linewidth", 0)        
        kwargs.setdefault("color", "red")
        xticks = arange(len(values)) + kwargs["width"] / 2.0
        self.axes.bar(xticks, values, **kwargs)
        self.axes.set_xticks(xticks)
        # Pad the right side of the graph if the last value is zero. Otheriwse,
        # the graph ends at the final xtick label, which looks ugly.
        if values[-1] == 0:
            _, xmax = self.axes.set_xlim()
            self.axes.set_xlim(xmax=xmax + kwargs["width"] / 2.0)

        max_value = max(values)
        tick_interval = round((max_value / 4.0) + 1)
        self.axes.set_yticks(arange(tick_interval, max_value + tick_interval, 
                                    tick_interval))
        self.axes.set_ylim(ymax=max_value + 0.5 * tick_interval)
        for label in self.axes.get_yticklabels():
            label.set_size("small")
        # Add exact numeric values above each bar. The text padding is based 
        # on the average height of non-zero bars. This gives a reasonable
        # padding for most data, but looks ugly when one bar is *much* larger
        # than the others. Note that bool() can be used as the filter function
        # since bool(0) == False.
        avg = lambda s: sum(s) / len(s)
        avg_height = avg(filter(bool, values))
        pad = avg_height * 1.05 - avg_height
        for i in range(len(values)):
            height = values[i]
            if height == 0:
                continue
            self.axes.text(xticks[i], height + pad, "%d" % height, ha="center", 
                           va="bottom", fontsize="small")
            
    def plot_histogram(self, values, **kwargs):
        self.axes.grid(True)
        kwargs.setdefault("facecolor", "red")
        kwargs.setdefault("alpha", 0.7)
        self.axes.hist(values, **kwargs)

    def plot_piechart(self, values, **kwargs):
        # Pie charts look better on a square canvas, but the following does not
        # seem enough to achieve this, probably due to interplay with the Qt
        # layout manager. TODO: fix this.
        self.figure.set_size_inches(self.figure.get_figheight(),
                                 self.figure.get_figheight())
        self.axes.set_xlim(0.1, 0.8)
        self.axes.set_ylim(0.1, 0.8)
        # Only print percentage on wedges > 5%.
        kwargs.setdefault("autopct", lambda x: "%1.1f%%" % x if x > 5 else "")
        self.axes.pie(values, **kwargs)

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
