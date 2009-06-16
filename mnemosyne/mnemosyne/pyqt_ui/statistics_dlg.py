#
# statistics_dlg.py <mike@peacecorps.org.cv>
#

from PyQt4 import QtGui
from numpy import arange

from mnemosyne.libmnemosyne.translator import _
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


class StatGraphBase(object):

    """Base class for statistics graphs.

    Specifies a Factory interface for creating graphs. In most cases,
    subclasses only need to override __init__ to assign the appropriate graph
    type to self.graph and values(...) to generate the values to be plotted.
    Subclasses can also specify a dict of keyword args that will be passed to
    the graph's plot method by overriding the kwargs method.

    """

    def __init__(self, parent, scope, colour="white"):
        self.graph = MatplotlibCanvas(parent, colour=colour)
        self.scope = scope
        self.title = ""
        self.xlabel = ""
        self.ylabel = ""

    def make_graph(self):

        "Generate the plot and return an instance of MatplotlibCanvas."
        
        values = self.values()
        kwargs = self.kwargs(values)
        self.prepare_axes(values)
        if self.is_valid(values):
            self.graph.plot(values, **kwargs)
        else:
            self.graph.display_message(_("No stats available."))
        return self.graph

    def values(self): # TODO PB: best design? Make a property?
        
        "Return the values to be plotted."
        
        return []

    def kwargs(self, values): # TODO PB: best design? Why not call self.values?
        
        """Return keyword args for the plotting method. Note that they can
        depend on the values to be plotted.

        """
        
        return {}

    def prepare_axes(self, values):
        
        """Set the graph title, x- and y-labels, and any other special
        formatting required."""

        self.graph.axes.set_title(self.title)
        self.graph.axes.set_xlabel(self.xlabel)
        self.graph.axes.set_ylabel(self.ylabel)

    def is_valid(self, values):        
        return max(values) > 0


class ScheduleGraph(StatGraphBase):

    """Graph of card scheduling statistics."""

    scope_err_msg = _("""Scope must be one of ("next_week", "next_month", " +\
                    ""next_year")""")

    def __init__(self, parent, scope, color=None):
        StatGraphBase.__init__(self, parent, scope, colour)
        self.ylabel = "Number of cards scheduled"
        if self.scope == "all_time":
            self.graph = Histogram(parent, colour=colour)
            self.values = self.values_for_histogram
            self.kwargs = self.kwargs_for_histogram
            self.prepare_axes = self.prepare_axes_for_histogram
            self.xlabel = "Days"
        else:
            self.graph = BarGraph(parent, colour=colour)
            self.values = self.values_for_bargraph
            self.kwargs = self.kwargs_for_bargraph
            self.prepare_axes = self.prepare_axes_for_bargraph

    def is_valid(self, values): # For histogram
        return len(values) > 0
    
    def values_for_bargraph(self):
        if self.scope == "next_week":
            range_ = range(0, 7, 1)
        elif self.scope == "next_month": 
            range_ = range(6, 28, 7)
        elif self.scope == "next_year":  
            range_ = range(30, 365, 30)
        else:
            raise ArgumentError, ScheduleGraph.scope_err_msg
        old_cumulative = 0
        values = []
        for days in range_:
            cumulative = self.database().scheduled_count(days)
            values.append(cumulative - old_cumulative)
            old_cumulative = cumulative
        return values

    def values_for_histogram(self):
        iton = lambda i: (i + abs(i)) / 2 # i < 0 ? 0 : i
        values = [iton(c.days_until_next_rep) 
                  for c in self.database().get_all_cards()]
        return values

    def kwargs_for_bargraph(self, values):
        return dict(width=1.0, align="center", alpha=0.7, linewidth=0, 
                    color="red")

    def kwargs_for_histogram(self, values):
        kwargs = {}
        if len(values) != 0:
            kwargs["range"] = (min(values) - 0.5, max(values) + 0.5)
            kwargs["bins"] = max(values) - min(values) + 1
        return kwargs

    def prepare_axes_for_bargraph(self, values):
        StatGraphBase.prepare_axes(self, values)
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
        else:
            raise ArgumentError, ScheduleGraph.scope_err_msg
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_xticklabels(xticklabels, fontsize="small")

    def prepare_axes_for_histogram(self, values):
        StatGraphBase.prepare_axes(self, values)
        if len(values) != 0:
            self.graph.axes.set_xticks(arange(max(values) + 1))


class GradesGraph(StatGraphBase):

    "Graph of card grade statistics."

    def __init__(self, parent, scope, colour=None):
        StatGraphBase.__init__(self, parent, scope, colour)
        #self.graph = PieChart(parent, colour=colour)
        self.graph = Histogram(parent, colour=colour)
        self.title = "Number of cards per grade level"

    def values(self):
        grades = [0] * 6 # There are six grade levels
        for card in self.database().get_all_cards():
            cat_names = [c.name for c in card.tags]
            if self.scope == "grades_all_tags" or self.scope in cat_names:
                grades[card.grade] += 1
        return grades

    #def kwargs(self, values):
    #    return dict(explode=(0.05, 0, 0, 0, 0, 0),
    #                labels=["Grade %d" % g if values[g] > 0 else "" 
    #                          for g in range(0, len(values))],
    #                colors=("r", "m", "y", "g", "c", "b"), 
    #                shadow=True)


class EasinessGraph(StatGraphBase):

    "Graph of card easiness statistics."

    def __init__(self, parent, scope, color=None):
        StatGraphBase.__init__(self, parent, scope, colour)
        self.graph = Histogram(parent, colour=colour)
        self.xlabel = "Easiness"
        self.ylabel = "Number of Cards"

    def values(self):
        values = []
        for card in self.database().get_all_cards():
            cat_names = [c.name for c in card.tags]
            if self.scope == "easiness_all_tags" or self.scope in cat_names:
                values.append(card.easiness)
        return values
    
    def is_valid(self, values):
        return len(values) > 0


class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    def __init__(self, parent=None, name=None, modal=0):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        colour = self.background_colour()
        tags = sorted(self.database().tag_names(), cmp=numeric_string_cmp)

        # Add tags to comboBox and corresponding pages to stackedWidget
        # for grades and easiness tabs.
        self.add_items_to_combobox(tags, self.grades_combo)
        self.add_pages_to_stackedwidget(tags, self.grades_stack)
        self.add_items_to_combobox(tags, self.easiness_combo)
        self.add_pages_to_stackedwidget(tags, self.easiness_stack)

        pages = lambda sw: [sw.widget(i) for i in range(0, sw.count())]
        self.add_graphs_to_pages(ScheduleGraph, pages(self.sched_stack), colour)
        self.add_graphs_to_pages(GradesGraph, pages(self.grades_stack), colour)
        self.add_graphs_to_pages(EasinessGraph, pages(self.easiness_stack), 
                                 colour)

    def add_items_to_combobox(self, names, combo):
        
        "Add each name in the list to the specified combobox."
        
        for name in names:
            combo.addItem(QString(name))

    def add_pages_to_stackedwidget(self, names, stack):
        
        """Create and add a list of widgets with specified objectNames to the 
        specified stacked widget.
        
        names -- the list of strings to use as objectNames for the widgets
                 that will be added to the stack.
        stack -- a QStackedWidget.

        """
        for name in names:
            widget = QWidget()
            widget.setObjectName(name)
            stack.addWidget(widget)
        
    def add_graphs_to_pages(self, graph_factory, pages, bg_colour=None):
        
        """Add the graphs created by the graph_factory to the specified stacked
        widget pages.
        
        graph_factory -- a factory object with method 'make_graph' that will
                         return a graph of the appropriate type for the given
                         scope.
        pages -- a list of pages of a QStackedWidget to which the graphs will
                 be added.

        Keyword Arguments:
        bg_colour -- the background colour for the graph (default None).

        """
        
        scopes = [str(page.objectName()) for page in pages]
        for parent, scope in zip(pages, scopes):
            layout = QtGui.QVBoxLayout(parent)
            factory = graph_factory(parent, scope, colour=bg_colour)
            graph = factory.make_graph()
            layout.addWidget(graph)

    def background_colour(self):
        
        """Return this window's background colour.
        
        Sadly, this won't work on OS X, XP, or Vista since they use native
        theme engines for drawing, rather than the palette. See:
        http://doc.trolltech.com/4.4/qapplication.html#setPalette

        """
        
        if self.style().objectName() == "macintosh (Aqua)":
            bg_colour = "0.91"
        else:
            r, g, b, a = self.palette().color(self.backgroundRole()).getRgb()
            bg_colour = map(lambda x: x / 255.0, (r, g, b))
        return bg_colour
