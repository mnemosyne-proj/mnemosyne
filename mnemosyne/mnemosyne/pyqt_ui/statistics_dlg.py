#
# statistics_dlg.py <mike@peacecorps.org.cv>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from ui_statistics_dlg import Ui_StatisticsDlg


class MplCanvas(FigureCanvas):

    """Base canvas class for creating graphs with Matplotlib."""
    
    def __init__(self, parent, width=5, height=4, dpi=100, color=None):
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

    def plot(self, values, **kwargs):
        pass


class Histogram(MplCanvas):

    def plot(self, values, **kwargs):
        if len(values) == 0:
            self.display_message('No stats available.')
            return
        self.axes.grid(True)
        self.axes.hist(values, facecolor='red', alpha=0.7, **kwargs)


class PieChart(MplCanvas):

    def __init__(self, parent=None, width=4, height=4, dpi=100, color=None):
        # Pie charts look better on a square canvas.
        MplCanvas.__init__(self, parent, width, height, dpi, color)

    def plot(self, values, **kwargs):
        if max(values) == 0:
            self.display_message('No stats available.')
            return
        # Only print percentage on wedges > 5%.
        autopctfn = lambda x: '%1.1f%%' % x if x > 5 else ''
        self.axes.pie(values, autopct=autopctfn, **kwargs)


class BarGraph(MplCanvas):

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


class StatGraphBase(object):

    """Base class for statistics graphs.

    Specifies a "Factory" interface for creating graphs. Subclasses will only
    need to override make_graph if the type of graph returned depends on the 
    scope argument or if the class needs to do special formatting of the graph
    (e.g. ScheduleGraph below). In most cases, subclasses only need to override 
    __init__ to assign the appropriate graph type to self.graph, and values_for
    to generate the values to be plotted. Subclasses can also specify a dict of
    keyword args that will be passed to the graph's plot method by overriding
    the kwargs_for method.

    """

    def __init__(self, parent, color='white'):
        self.graph = MplCanvas(parent, color=color)
        self.title = ''
        self.xlabel = ''
        self.ylabel = ''

    def make_graph(self, scope):
        self.graph.axes.set_title(self.title)
        self.graph.axes.set_xlabel(self.xlabel)
        self.graph.axes.set_ylabel(self.ylabel)
        values = self.values_for(scope)
        kwargs = self.kwargs_for(scope, values)
        self.graph.plot(values, **kwargs)
        return self.graph

    def values_for(self, scope):
        return []

    def kwargs_for(self, scope, values):
        return {}


class ScheduleGraph(StatGraphBase):

    """Graph of card scheduling statistics."""

    def __init__(self, parent, color=None):
        StatGraphBase.__init__(self, parent, color)

    def make_graph(self, scope):
        parent = self.graph.parent()
        color = self.graph.fig.get_facecolor()
        if scope == 'all_time':
            self.graph = Histogram(parent, color=color)
            self.make_histogram(scope)
        else:
            self.graph = BarGraph(parent, color=color)
            self.make_bargraph(scope)
        return self.graph

    def make_bargraph(self, scope):

        """Create a bar graph of card scheduling statistics."""

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

        self.graph.axes.set_ylabel('Number of Cards Scheduled')
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_xticklabels(xticklabels, fontsize='small')

        values = []
        old_cumulative = 0
        for days in range_:
            cumulative = database().scheduled_count(days)
            values.append(cumulative - old_cumulative)
            old_cumulative = cumulative

        self.graph.plot(values, **kwargs)

    def make_histogram(self, scope):

        """Create a histogram of card scheduling statistics."""

        self.graph.axes.set_ylabel('Number of Cards Scheduled')
        self.graph.axes.set_xlabel('Days')
        iton = lambda i: (i + abs(i)) / 2 # i < 0 ? 0 : i
        values = [iton(c.days_until_next_rep) for c in database().cards]
        kwargs = dict()
        if len(values) != 0:
            kwargs['range'] = (min(values) - 0.5, max(values) + 0.5)
            kwargs['bins'] = max(values) - min(values) + 1
            self.graph.axes.set_xticks(arange(max(values) + 1))
        self.graph.plot(values, **kwargs)


class GradesGraph(StatGraphBase):

    """Graph of card grade statistics."""

    def __init__(self, parent, color=None):
        StatGraphBase.__init__(self, parent, color)
        self.graph = PieChart(parent, color=color)
        self.title = 'Number of cards per grade level'

    def values_for(self, scope):
        grades = [0] * 6 # There are six grade levels
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'grades_all_categories' or scope in cat_names:
                grades[card.grade] += 1
        return grades

    def kwargs_for(self, scope, values):
        return dict(explode=(0.05, 0, 0, 0, 0, 0),
                    labels=['Grade %d' % g if values[g] > 0 else '' 
                              for g in range(0, len(values))],
                    colors=('r', 'm', 'y', 'g', 'c', 'b'), 
                    shadow=True)


class EasinessGraph(StatGraphBase):

    """Graph of card easiness statistics."""

    def __init__(self, parent, color=None):
        StatGraphBase.__init__(self, parent, color)
        self.graph = Histogram(parent, color=color)
        self.xlabel = 'Easiness'
        self.ylabel = 'Number of Cards'

    def values_for(self, scope):
        values = []
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'easiness_all_categories' or scope in cat_names:
                values.append(card.easiness)
        return values


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
        
    def add_graphs_to_pages(self, graph_factory, pages, bg_color=None):
        """
        
        graph_factory -- a factory object with method 'make_graph' that will
                         return a graph of the appropriate type for the given
                         scope.
        pages -- a list of pages of a QStackedWidget to which the graphs will
                 be added.

        Keyword Arguments:
        bg_color -- the background color for the graph (default None).

        """
        scopes = [str(page.objectName()) for page in pages]
        for parent, scope in zip(pages, scopes):
            layout = QVBoxLayout(parent)
            factory = graph_factory(parent, color=bg_color)
            graph = factory.make_graph(scope)
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
