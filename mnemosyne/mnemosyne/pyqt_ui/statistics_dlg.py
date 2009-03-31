#
# statistics_dlg.py <mike@peacecorps.org.cv>
#
# TODO: Refactor graph classes into BarGraph, PieChart, and Histogram, rather
# than ScheduleGraph, GradesGraph, and EasinessGraph
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from ui_statistics_dlg import Ui_StatisticsDlg


class StatGraph(FigureCanvas):

    """Base canvas class for creating graphs with Matplotlib."""
    
    def __init__(self, parent, width=5, height=4, dpi=100, color='white', 
                 scope=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=color, 
                          edgecolor=color)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.MinimumExpanding, 
                                   QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        #FigureCanvas.updateGeometry(self)

    def display_message(self, msg):
        self.axes.clear()
        self.axes.set_xticklabels('')
        self.axes.set_yticklabels('')
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, msg, transform=self.axes.transAxes,
                       horizontalalignment='center', verticalalignment='center')


class Histogram(StatGraph):

    def plot(self, values, **kwargs):
        if len(values) == 0:
            self.display_message('No stats available.')
            return
        kwargs['facecolor'] = 'red'
        kwargs['alpha'] = 0.7
        self.axes.grid(True)
        self.axes.hist(values, **kwargs)


class PieChart(StatGraph):

    def __init__(self, parent=None, width=4, height=4, dpi=100, color='white'):
        # Pie charts look better on a square canvas.
        StatGraph.__init__(self, parent, width, height, dpi, color)

    def plot(self, values, **kwargs):
        if max(values) == 0:
            self.display_message('No stats available.')
            return

        # Only print percentage on wedges > 5%.
        autopctfn = lambda x: '%1.1f%%' % x if x > 5 else ''
        self.axes.pie(values, autopct=autopctfn, **kwargs)


class BarGraph(StatGraph):

    def plot(self, values, **kwargs):
        if max(values) == 0:
            self.display_message('No stats available.')
            return
        xticks = arange(len(values)) + kwargs['width'] / 2.0
        self.axes.bar(xticks, values, **kwargs)
        self.axes.set_xticks(xticks)

        # Pad the right side of the graph if the last value is zero. Otheriwse,
        # the graph ends at the final xtick label, which looks ugly.
        if values[-1] == 0:
            _, xmax = self.axes.set_xlim()
            self.axes.set_xlim(xmax=xmax+kwargs['width']/2.0)

        max_value = max(values)
        tick_interval = round((max_value / 4.0) + 1)
        self.axes.set_yticks(arange(tick_interval, max_value + tick_interval, 
                                    tick_interval))
        self.axes.set_ylim(ymax=max_value + 0.5 * tick_interval)
        for label in self.axes.get_yticklabels():
            label.set_size('small')

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
            if height == 0: continue
            self.axes.text(xticks[i], height + pad, '%d' % height, ha='center', 
                           va='bottom', fontsize='small')


class ScheduleGraph(object):

    """Graph of card scheduling statistics."""

    def make_graph(cls, parent, scope=None, color='white'):
        if scope == 'all_time':
            return cls.make_histogram(parent, scope, color)
        else:
            return cls.make_bargraph(parent, scope, color)
    make_graph = classmethod(make_graph)

    def make_bargraph(self, parent, scope, color):

        """Create a bar graph of card scheduling statistics."""

        graph = BarGraph(parent, color=color)
        kwargs = dict(width=1.0, align='center', alpha=0.7, linewidth=0)
        xticklabels = lambda i, j: map(lambda x: "+%d" % x, range(i, j))
        if scope == 'next_week':
            range_ = range(0, 7, 1)
            xlabel = 'Days' 
            xticklabels = ['Today'] + xticklabels(1, 7)
            kwargs['color'] = ('r', 'g', 'b', 'c', 'm', 'y', 'k')
        elif scope == 'next_month': 
            range_ = range(6, 28, 7)
            xlabel = 'Weeks'
            xticklabels = ['This week'] + xticklabels(1, 4)
            kwargs['color'] = ('r', 'g', 'b', 'c')
        elif scope == 'next_year':  
            range_ = range(30, 365, 30)
            xlabel = 'Months'
            xticklabels = xticklabels(0, 12)
            kwargs['color'] = 'red'
        else:
            raise ArgumentError, "scope must be one of ('next_week', 'next_month', 'next_year')"

        graph.axes.set_ylabel('Number of Cards Scheduled')
        graph.axes.set_xlabel(xlabel)
        graph.axes.set_xticklabels(xticklabels, fontsize='small')

        values = []
        old_cumulative = 0
        for days in range_:
            cumulative = database().scheduled_count(days)
            values.append(cumulative - old_cumulative)
            old_cumulative = cumulative

        graph.plot(values, **kwargs)
        return graph
    make_bargraph = classmethod(make_bargraph)

    def make_histogram(cls, parent, scope, color):

        """Create a histogram of card scheduling statistics."""

        graph = Histogram(parent, color=color)
        graph.axes.set_ylabel('Number of Cards Scheduled')
        graph.axes.set_xlabel('Days')
        days_since_start = database().days_since_start()
        iton = lambda i: (i + abs(i)) / 2 # i < 0 ? 0 : i
        values = [iton(c.next_rep - days_since_start) for c in database().cards]
        kwargs = dict()
        if len(values) != 0:
            kwargs['range'] = (min(values) - 0.5, max(values) + 0.5)
            kwargs['bins'] = max(values) - min(values) + 1
            graph.axes.set_xticks(arange(max(values) + 1))
        graph.plot(values, **kwargs)
        return graph
    make_histogram = classmethod(make_histogram)


class GradesGraph(object):

    """Graph of card grade statistics."""

    def make_graph(cls, parent, scope, color=None):

        """Create a pie chart of card grade statistics."""

        graph = PieChart(parent, color=color)
        graph.axes.set_title('Number of cards per grade level')
        grades = [0] * 6 # There are six grade levels
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'grades_all_categories' or scope in cat_names:
                grades[card.grade] += 1

        kwargs = dict(explode=(0.05, 0, 0, 0, 0, 0),
                      labels=['Grade %d' % g if grades[g] > 0 else '' 
                              for g in range(0, len(grades))],
                      colors=('r', 'm', 'y', 'g', 'c', 'b'), shadow=True)

        graph.plot(grades, **kwargs)
        return graph
    make_graph = classmethod(make_graph)


class EasinessGraph(object):

    """Graph of card easiness statistics."""

    def make_graph(cls, parent, scope=None, color='white'):
        graph = Histogram(parent, color=color)
        graph.axes.set_ylabel('Number of cards')
        graph.axes.set_xlabel('Easiness')
        values = []
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'easiness_all_categories' or scope in cat_names:
                values.append(card.easiness)
        graph.plot(values)
        return graph
    make_graph = classmethod(make_graph)


class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    def __init__(self, parent=None, name=None, modal=0):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        color = self.background_color()
        categories = sorted(database().category_names(), cmp=numeric_string_cmp)

        # Add categories to comboBox and corresponding pages to stackedWidget
        # for grades and easiness tabs.
        self.add_items_to_combobox(categories, self.grades_combo)
        self.add_pages_to_stackedwidget(categories, self.grades_stack)
        self.add_items_to_combobox(categories, self.easiness_combo)
        self.add_pages_to_stackedwidget(categories, self.easiness_stack)

        pages = lambda sw: [sw.widget(i) for i in range(0, sw.count())]
        self.add_graphs_to_pages(ScheduleGraph, pages(self.sched_stack), color)
        self.add_graphs_to_pages(GradesGraph, pages(self.grades_stack), color)
        self.add_graphs_to_pages(EasinessGraph, pages(self.easiness_stack), 
                                 color)

    def add_items_to_combobox(self, names, combo):
        """Add each name in the list to the specified comboBox."""
        for name in names:
            combo.addItem(QString(name))

    def add_pages_to_stackedwidget(self, names, stack):
        """
        Create and add a list of widgets with specified objectNames to the 
        specified stacked widget.
        
        names -- the list of strings to use as objectNames for the widgets
                 that will be added to the stack.
        stack -- a QStackedWidget.

        """
        for name in names:
            widget = QWidget()
            widget.setObjectName(name)
            stack.addWidget(widget)
        
    def add_graphs_to_pages(self, graph_type, pages, bg='white'):
        """
        Add a graph of type <graph_type> to each stackedWidget page.
        
        graph_type -- the type of graph to add. Must be an actual classname.
        pages -- a list of widgets that will be used as parent widgets for
                 the graphs.

        Keyword Arguments:
        bg -- the background color for the graph (default 'white').

        """
        names = [str(page.objectName()) for page in pages]
        for parent, name in zip(pages, names):
            layout = QVBoxLayout(parent)
            graph = graph_type.make_graph(parent, scope=name, color=bg)
            layout.addWidget(graph)

    def background_color(self):
        """
        Return this window's background color.
        
        Sadly, this won't work on OS X, XP, or Vista since they use native
        theme engines for drawing, rather than the palette. See:
        http://doc.trolltech.com/4.4/qapplication.html#setPalette

        """
        if self.style().objectName() == 'macintosh (Aqua)':
            bg_color = '0.91'
        else:
            r, g, b, _ = self.palette().color(self.backgroundRole()).getRgb()
            bg_color = map(lambda x: x / 255.0, (r, g, b))
        return bg_color
