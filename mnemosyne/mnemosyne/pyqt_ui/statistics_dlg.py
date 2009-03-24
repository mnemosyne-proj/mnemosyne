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
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, color='white', 
                 scope=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=color, 
                          edgecolor=color)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.MinimumExpanding, 
                                   QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.generate_figure(scope)
        #FigureCanvas.updateGeometry(self)

    def generate_figure(self, scope):
        pass

    def display_message(self, msg):
        self.axes.clear()
        self.axes.set_xticklabels('')
        self.axes.set_yticklabels('')
        self.axes.set_xticks((0.0,))
        self.axes.set_yticks((0.0,))
        self.axes.text(0.5, 0.5, msg, transform=self.axes.transAxes,
                       horizontalalignment='center', verticalalignment='center')


class ScheduleGraph(StatGraph):

    """Graph of card scheduling statistics."""

    def generate_figure(self, scope):
        if scope == 'all_time':
            self.generate_histogram()
        else:
            self.generate_bar_graph(scope)

    def generate_bar_graph(self, scope):

        """Create a bar graph of card scheduling statistics."""

        BAR_WIDTH = 1.0
        HALF_WIDTH = BAR_WIDTH / 2.0
        xticklabels = lambda i, j: map(lambda x: "+%d" % x, range(i, j))
        scope_vars_map = {'next_week': {'range': range(0, 7, 1), 
                                        'bar_colors': ('r', 'g', 'b', 'c', 'm', 
                                                       'y', 'k'),
                                        'xlabel': 'Days', 
                                        'xticklabels': ['Today'] + 
                                                       xticklabels(1, 7)},
                          'next_month': {'range': range(6, 28, 7),
                                         'bar_colors': ('r', 'g', 'b', 'c'),
                                         'xlabel': 'Weeks',
                                         'xticklabels': ['This week'] + 
                                                        xticklabels(1, 4)},
                          'next_year':  {'range': range(30, 365, 30),
                                         'bar_colors': 'red',
                                         'xlabel': 'Months',
                                         'xticklabels': xticklabels(0, 12)}}
        scope_vars = scope_vars_map[scope]
        range_ = scope_vars['range']
        self.axes.set_ylabel('Number of Cards Scheduled')
        self.axes.set_xlabel(scope_vars['xlabel'])
        values = []
        old_cumulative = 0
        for days in range_:
            cumulative = database().scheduled_count(days)
            values.append(cumulative - old_cumulative)
            old_cumulative = cumulative

        # No cards scheduled for this time frame.
        if max(values) == 0:
            self.display_message('No stats available.')
            return

        xticks = arange(len(values)) + HALF_WIDTH
        bar_colors = ('r', 'g', 'b', 'c', 'm', 'y', 'k')
        self.axes.bar(xticks, values, BAR_WIDTH, align='center', 
                      color=bar_colors, alpha=0.7, linewidth=0)
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(scope_vars['xticklabels'], fontsize='small')

        # Pad the right side of the graph if the last value is zero. Otheriwse,
        # the graph ends at the final xtick label, which looks ugly.
        if values[-1] == 0:
            _, xmax = self.axes.set_xlim()
            self.axes.set_xlim(xmax=xmax+HALF_WIDTH)

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

    def generate_histogram(self):

        """Create a histogram of card scheduling statistics."""

        self.axes.set_ylabel('Number of Cards Scheduled')
        self.axes.set_xlabel('Days')
        xs = [c.next_rep for c in database().cards]
        if len(xs) == 0:
            self.display_message('No stats available.')
            return
        self.axes.hist(xs, facecolor='red', alpha=0.7)
        self.axes.grid(True)


class GradesGraph(StatGraph):

    """Graph of card grade statistics."""

    def __init__(self, parent=None, width=4, height=4, dpi=100, color='white', 
                 scope=None):
        # Pie charts look better on a square canvas.
        StatGraph.__init__(self, parent, width, height, dpi, color, scope)

    def generate_figure(self, scope):

        """Create a pie chart of card grade statistics."""

        self.axes.set_title('Number of cards per grade level')
        grades = [0] * 6 # There are six grade levels
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'grades_all_categories' or scope in cat_names:
                grades[card.grade] += 1

        if max(grades) == 0:
            self.display_message('No stats available.')
            return

        # Only print percentage on wedges > 5%.
        autopctfn = lambda x: '%1.1f%%' % x if x > 5 else ''
        self.axes.pie(grades, explode=(0.05, 0, 0, 0, 0, 0), autopct=autopctfn, 
                      labels=['Grade %d' % g if grades[g] > 0 else '' 
                              for g in range(0, len(grades))],
                      colors=('r', 'm', 'y', 'g', 'c', 'b'), shadow=True)
 

class EasinessGraph(StatGraph):

    """Graph of card easiness statistics."""

    def generate_figure(self, scope):
        """
        Create a histogram of easiness values for every card.
        
        scope -- a category name or the string 'easiness_all_categories'

        """
        self.axes.set_ylabel('Number of cards')
        self.axes.set_xlabel('Easiness')
        xs = []
        for card in database().cards:
            cat_names = [c.name for c in card.fact.cat]
            if scope == 'easiness_all_categories' or scope in cat_names:
                xs.append(card.easiness)
        if len(xs) == 0:
            self.display_message('No stats available.')
            return
        self.axes.hist(xs, facecolor='red', alpha=0.7)
        self.axes.grid(True)
        

class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    # TODO: Factor out duplicated code from add_*_stats() methods.

    def __init__(self, parent=None, name=None, modal=0):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.add_schedule_stats()
        self.add_grades_stats()
        self.add_easiness_stats()

    def add_schedule_stats(self):
        """Add graphs for schedule statistics to the sched tab."""
        bg_color = self.background_color()
        scopes = self.page_names_for_stacked_widget(self.sched_stack)
        widgets = self.pages_for_stacked_widget(self.sched_stack)
        self.add_graphs_for_scopes(ScheduleGraph, scopes, widgets, bg_color)

    def add_grades_stats(self):
        """
        Add graphs for grade statistics to the grade tab.

        Fist, add items to the QComboBox and corresponding pages to the 
        QStackedWidget for each category in the database. Then, add the graph
        for each category to the pages of the stacked widget.

        """
        # TODO: get rid of duplicate code (see the update_categories_combobox
        # method in add_cards_dlg.py) by overriding QComboBox's sorting method.
        sorted_categories = sorted(database().category_names(), 
                                   cmp=numeric_string_cmp)
        self.add_items_to_combo_box(sorted_categories, self.grades_combo)
        self.add_pages_to_stacked_widget(sorted_categories, self.grades_stack)
        bg_color = self.background_color()
        scopes = self.page_names_for_stacked_widget(self.grades_stack)
        widgets = self.pages_for_stacked_widget(self.grades_stack)
        self.add_graphs_for_scopes(GradesGraph, scopes, widgets, bg_color)

    def add_easiness_stats(self):
        """
        Add graphs for easiness statistics to the easiness tab.

        """
        sorted_categories = sorted(database().category_names(), 
                                   cmp=numeric_string_cmp)
        self.add_items_to_combo_box(sorted_categories, self.easiness_combo)
        self.add_pages_to_stacked_widget(sorted_categories, self.easiness_stack)
        bg_color = self.background_color()
        scopes = self.page_names_for_stacked_widget(self.easiness_stack)
        widgets = self.pages_for_stacked_widget(self.easiness_stack)
        self.add_graphs_for_scopes(EasinessGraph, scopes, widgets, bg_color)
        
    def add_items_to_combo_box(self, items, combo):
        """
        Add each item in list to the specified combo box and stack widget.
        
        items -- a list of strings that will be used as both the combo box
                 text and the new stack widget page name.
        combo -- the QComboBox to which the items will be added.

        """
        for name in items:
            combo.addItem(QString(name))

    def add_pages_to_stacked_widget(self, names, stack):
        """
        Create and add a list of widgets with specified objectNames to the 
        specified stacked widget. Return a list of the created widgets.
        
        names -- the list of strings to use as objectNames for the widgets
                 that will be added to add to the stack.
        stack -- a QStackedWidget.

        """
        widgets = []
        for name in names:
            widget = QWidget()
            widget.setObjectName(name)
            #setattr(self, str(id(widget)) + '_' + name, widget)
            stack.addWidget(widget)
            widgets.append(widget)
        return widgets
        
    def add_graphs_for_scopes(self, graph_type, scopes, widgets, bg='white'):
        """
        Add a graph of type <graph_type> for each scope.
        
        graph_type -- the type of graph to add. Must be an actual classname.
        scopes -- a list of keywords on which the graph specializes it's output,
                  e.g. ('daily', 'weekly', 'monthly', 'all_time').
        widgets -- a list of widgets that will be used as parent widgets for
                   the graphs.

        Keyword Arguments:
        bg -- the background color for the graph (default 'white').

        Raises:
        ArgumentError if len(scopes) != len(widgets)
        """
        if len(scopes) != len(widgets):
            raise ArgumentError, "Widgets and scopes lists must be same length."
        for i, name in enumerate(scopes):
            parent = widgets[i]
            layout = QVBoxLayout(parent)
            #layout_name = str(id(parent)) + '_' + name + '_layout'
            #layout.setObjectName(layout_name)
            #setattr(self, layout_name, layout)
            graph = graph_type(parent, scope=name, color=bg)
            #graph_name = str(id(parent)) + '_' + name + '_graph'
            #graph.setObjectName(graph_name)
            #setattr(self, str(id(graph)) + '_' + graph_name, graph)
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

    def page_names_for_stacked_widget(self, stack):
        """
        Return a list of page names for the given stacked widget.
        
        stack -- a QStackWidget

        """
        # TODO: move this function into utils.py
        names = []
        for i in range(0, stack.count()):
            names.append(stack.widget(i).objectName().__str__())
        return names

    def pages_for_stacked_widget(self, stack):
        """
        Return widget objects that make up the pages for the specified stack.
        
        stack -- a QStackWidget.
        """
        widgets = []
        for i in range(0, stack.count()):
            widgets.append(stack.widget(i))
        return widgets
        
