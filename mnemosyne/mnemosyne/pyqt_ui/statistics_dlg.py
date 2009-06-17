#
# statistics_dlg.py <mike@peacecorps.org.cv>, <Peter.Bienstman@UGent.be>
#

from numpy import arange
from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import numeric_string_cmp

from mnemosyne.pyqt_ui.matplotlib_canvas import Histogram, PieChart, BarGraph 
from mnemosyne.pyqt_ui.ui_statistics_dlg import Ui_StatisticsDlg

# TODO: Make graph creation lazy.
# Now all the graphs are created when the widget is opened, which could take a
# long time on large databases. So, we should get rid of the stacked widgets
# and only use one widget which we redraw once the user changes the combobox.
# Also, rather than making a graph upon creation of the widget, we should
# try to do this in the paint method, such that it only gets created when the
# user changes the tabs.

# TODO: Add graphs which include data from the history: retention rate, cards
# scheduled in the past, repetitions per day, cards added per day, ...


class Graph(object):

    """Base class for statistics graphs.

    In most cases, subclasses only need to override __init__ to assign the
    appropriate graph type to self.graph and _calc_data(...) to generate the
    data to be plotted. Subclasses can also specify a dict of keyword args
    that will be passed to the graph's plot method by overriding the kwargs
    method.

    """

    def __init__(self, parent):
        self.graph = None # TODO: why not inheriting here?
        self.title = ""
        self.xlabel = ""
        self.ylabel = ""
        self._data = None

    @property
    def data(self):
        
        "The data to be plotted, lazily calculated."

        if self._data is None:
            self._calc_data()
        return self._data

    def _calc_data(self):
        raise NotImplementedError

    def generate_plot(self):        
        self.prepare_axes()
        if self.is_valid():
            self.graph.plot(self.data, **self.kwargs)
        else:
            self.graph.display_message(_("No stats available."))

    @property
    def kwargs(self):
        
        """Return keyword args for the plotting method. Note that they can
        depend on the data to be plotted.

        """
        
        return {}

    def prepare_axes(self):
        
        """Set the graph title, x- and y-labels, and any other special
        formatting required."""

        self.graph.axes.set_title(self.title)
        self.graph.axes.set_xlabel(self.xlabel)
        self.graph.axes.set_ylabel(self.ylabel)

    def is_valid(self):
        return max(self.data) > 0


class ScheduleGraph(Graph):

    "Graph of card scheduling statistics."

    def __init__(self, parent, scope):
        Graph.__init__(self, parent)
        self.ylabel = "Number of cards scheduled"
        self.scope = scope
        self.graph = BarGraph(parent)
        
    def _calc_data(self):
        if self.scope == "next_week":
            range_ = range(0, 7, 1)
        elif self.scope == "next_month": 
            range_ = range(6, 28, 7)
        elif self.scope == "next_year":  
            range_ = range(30, 365, 30)
        else:
            raise ArgumentError, "Invalid scope for ScheduleGraph."

        # TMP:
        import scipy
        self._data = scipy.random.randint(0, 200, (len(range_),))
        return
        
        old_cumulative = 0
        self._data = []
        for days in range_:
            cumulative = self.database().scheduled_count(days)
            self._data.append(cumulative - old_cumulative)
            old_cumulative = cumulative

    def prepare_axes(self):
        Graph.prepare_axes(self)
        xticklabels = lambda i, j: map(lambda x: "+%d" % x, range(i, j))
        if self.scope == "next_week":
            range_ = range(0, 7, 1)
            xlabel = "Days" 
            xticklabels = ["Today"] + xticklabels(1, 7)
        elif self.scope == "next_month": 
            range_ = range(6, 28, 7)
            xlabel = "Weeks"
            xticklabels = ["This week"] + xticklabels(1, 4)
        elif self.scope == "next_year":  
            range_ = range(30, 365, 30)
            xlabel = "Months"
            xticklabels = xticklabels(0, 12)
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_xticklabels(xticklabels, fontsize="small")


class IntervalGraph(Graph):

    "Histogram of card intervals."

    def __init__(self, parent):
        Graph.__init__(self, parent)
        self.xlabel = "Days"
        self.ylabel = "Number of cards scheduled"
        self.graph = Histogram(parent)
        
    def _calc_data(self):
        
        # TMP:
        import scipy
        self._data = scipy.random.randint(0, 200, (500, ))
        return
        
        iton = lambda i: (i + abs(i)) / 2 # i < 0 ? 0 : i
        self._data = [iton(c.days_until_next_rep) 
                    for c in self.database().get_all_cards()]

    @property
    def kwargs(self):
        kwargs = {}
        if len(self.data) != 0:
            kwargs["range"] = (min(self.data) - 0.5, max(self.data) + 0.5)
            kwargs["bins"] = max(self.data) - min(self.data) + 1
        return kwargs

    def prepare_axes(self):
        Graph.prepare_axes(self)
        if len(self.data) != 0:
            self.graph.axes.set_xticks(arange(max(self.data) + 1))

    def is_valid(self):
        return len(self.data) > 0


class GradesGraph(Graph):

    "Graph of card grade statistics."

    def __init__(self, parent, scope):
        Graph.__init__(self, parent)
        #self.graph = PieChart(parent)
        self.graph = Histogram(parent)
        self.title = "Number of cards per grade level"
        self.scope = scope

    def _calc_data(self):
        
        # TMP:
        import scipy
        import random
        self._data = [0] * 6
        for i in range(6):
            self._data[i] = random.randint(0, 2000)
        return

        
        self._data = [0] * 6 # There are six grade levels.
        for card in self.database().get_all_cards():
            cat_names = [c.name for c in card.tags]
            if self.scope == "grades_all_tags" or self.scope in cat_names:
                self._data[card.grade] += 1

    #def kwargs(self): # For piechart
    #    return dict(explode=(0.05, 0, 0, 0, 0, 0),
    #                labels=["Grade %d" % g if data[g] > 0 else "" 
    #                          for g in range(0, len(data))],
    #                colors=("r", "m", "y", "g", "c", "b"), 
    #                shadow=True)


class EasinessGraph(Graph):

    "Graph of card easiness statistics."

    def __init__(self, parent, scope):
        Graph.__init__(self, parent)
        self.graph = Histogram(parent)
        self.xlabel = "Easiness"
        self.ylabel = "Number of cards"
        self.scope = scope

    def _calc_data(self):
        
        # TMP:
        import scipy
        self._data = scipy.random.randint(0, 5.5, (600, ))
        return

        
        self._data = []
        for card in self.database().get_all_cards():
            tag_names = [tag.name for tag in card.tags]
            if self.scope == "easiness_all_tags" or self.scope in tag_names:
                self._data.append(card.easiness)

        
class StatisticsDlg(QtGui.QDialog, Ui_StatisticsDlg, Component):

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        tags = sorted(self.database().tag_names(), cmp=numeric_string_cmp)

        # Add tags to combobox and corresponding pages to stacked widget
        # for grades and easiness tabs.
        self.add_items_to_combobox(tags, self.grades_combo)
        self.add_pages_to_stacked_widget(tags, self.grades_stack)
        self.add_items_to_combobox(tags, self.easiness_combo)
        self.add_pages_to_stacked_widget(tags, self.easiness_stack)

        pages = lambda sw: [sw.widget(i) for i in range(0, sw.count())]
        self.add_graphs_to_pages(ScheduleGraph, pages(self.sched_stack))
        self.add_graphs_to_pages(GradesGraph, pages(self.grades_stack))
        self.add_graphs_to_pages(EasinessGraph, pages(self.easiness_stack))
        #self.add_graphs_to_pages(IntervalGraph, pages(self.easiness_stack))
        
    def add_items_to_combobox(self, names, combobox):
        for name in names:
            combobox.addItem(QtCore.QString(name))

    def add_pages_to_stacked_widget(self, names, stacked_widget):
        
        """Create and add a list of widgets with specified objectNames to the 
        specified stacked widget.
        
        names -- the list of strings to use as objectNames for the widgets
                 that will be added to the stack.
        stack -- a QStackedWidget.

        """
        for name in names:
            widget = QtGui.QWidget()
            widget.setObjectName(name)
            stacked_widget.addWidget(widget)
        
    def add_graphs_to_pages(self, graph, pages):
        scopes = [str(page.objectName()) for page in pages]
        for parent, scope in zip(pages, scopes):
            self.layout = QtGui.QVBoxLayout(parent)
            graph_obj = graph(parent, scope) # TODO: redesign
            graph_obj.generate_plot()
            self.layout.addWidget(graph_obj.graph)


