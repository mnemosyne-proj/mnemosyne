#
# matplotlib_canvas.py <mike@peacecorps.org.cv>
#

from PyQt4 import QtGui
from numpy import arange

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibCanvas(FigureCanvas):
    
    def __init__(self, parent, width=5, height=4, dpi=100, colour=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=colour, 
                          edgecolor=colour)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.MinimumExpanding, 
                                   QtGui.QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        #FigureCanvas.updateGeometry(self)

    def display_message(self, msg):
        self.axes.clear()
        self.axes.set_xticklabels("")
        self.axes.set_yticklabels("")
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, msg, transform=self.axes.transAxes,
                       horizontalalignment="center", verticalalignment="center")

    def plot(self, values, **kwargs):
        pass


class Histogram(MatplotlibCanvas):

    def plot(self, values, **kwargs):
        self.axes.grid(True)
        kwargs.setdefault("facecolor", "red")
        kwargs.setdefault("alpha", 0.7)
        self.axes.hist(values, **kwargs)


class PieChart(MatplotlibCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=100, colour=None):
        # Pie charts look better on a square canvas.
        MatplotlibCanvas.__init__(self, parent, width, height, dpi, colour)

    def plot(self, values, **kwargs):
        # Only print percentage on wedges > 5%.
        kwargs.setdefault("autopct", lambda x: "%1.1f%%" % x if x > 5 else "")
        self.axes.pie(values, **kwargs)


class BarGraph(MatplotlibCanvas):

    def plot(self, values, **kwargs):
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
