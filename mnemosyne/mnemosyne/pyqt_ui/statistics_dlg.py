#
# statistics_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class StatisticsDlg(QtGui.QDialog, Component):

    """A tab widget containing several statistics pages. The number and names
    of the tab pages are determined at run time.

    """

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.vbox_layout = QtGui.QVBoxLayout(self)
        self.tab_widget = QtGui.QTabWidget(parent)
        self.tab_widget.addTab(StatisticsPageWdgt(self, 1), "Page 1")
        self.tab_widget.addTab(StatisticsPageWdgt(self, 2), "Page 2")
        self.vbox_layout.addWidget(self.tab_widget)       
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addItem(QtGui.QSpacerItem(20, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.ok_button = QtGui.QPushButton(_("&OK"), self)
        self.button_layout.addWidget(self.ok_button)
        self.vbox_layout.addLayout(self.button_layout)
        self.connect(self.ok_button, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.tab_widget, QtCore.SIGNAL("currentChanged(int)"),
                     self.display_page)
        self.display_page(0)

    def display_page(self, page_index):
        page = self.tab_widget.widget(page_index)
        page.combobox.setCurrentIndex(0)
        page.display_variant(0)
        

class StatisticsPageWdgt(QtGui.QWidget):

    """A page in the StatisticsDlg tab widget. This page widget only contains
    a combobox to select different variants of the page. The widget that
    displays the statistics information itself is only generated when it
    becomes visible.

    """

    def __init__(self, parent, statistics_page):
        QtGui.QWidget.__init__(self, parent)
        self.statistics_page = statistics_page
        self.vbox_layout = QtGui.QVBoxLayout(self)
        self.combobox = QtGui.QComboBox(self)
        self.variant_ids = []
        self.variant_widgets = []
        self.current_variant_widget = None
        #if page.show_variant_in_combobox = True
        # Hide combobox if empty
        for variant_index in range(5):
            self.variant_ids.append(variant_index) # Variant_id
            self.variant_widgets.append(None)
            self.combobox.addItem(str(variant_index)) # Variant description    
        self.vbox_layout.addWidget(self.combobox)
        self.connect(self.combobox, QtCore.SIGNAL("currentIndexChanged(int)"),
                     self.display_variant)
        
    def display_variant(self, variant_index):

        "Lazy creation of the actual widget that displays the statistics."
        
        print 'display page', self.statistics_page, 'variant', variant_index
        if self.current_variant_widget:
            self.vbox_layout.removeWidget(self.current_variant_widget)
            self.current_variant_widget.hide()
        if not self.variant_widgets[variant_index]:
            print 'creating page', self.statistics_page, 'variant', variant_index
            # self.statistics_page.prepare(self.variant_ids[variant_index])
            self.variant_widgets[variant_index] = \
                QtGui.QLabel("page " + str(self.statistics_page) \
                + " variant " +  str(variant_index))
        self.current_variant_widget = self.variant_widgets[variant_index]
        self.vbox_layout.addWidget(self.current_variant_widget)
        self.current_variant_widget.show()



# TODO: move stuff below to libmnemosyne

from numpy import arange
from mnemosyne.libmnemosyne.utils import numeric_string_cmp

# <mike@peacecorps.org.cv>,

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
        self.graph = None
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

    def kwargs(self):
        kwargs = dict()
        if self.validate():
            kwargs['range'] = (0, 5)
            kwargs['bins'] = 6
        return kwargs

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


        kwargs = dict()
        if self.validate(values):
            diff = max(values) - min(values)
            if diff < 3:
                kwargs['range'] = (min(values) - 1, max(values) + 1)
            else:
                kwargs['range'] = (min(values), max(values))
            #kwargs['bins'] = max(values) - min(values) + 1
        return kwargs






