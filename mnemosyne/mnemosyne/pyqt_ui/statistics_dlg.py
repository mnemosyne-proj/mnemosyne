#
# statistics_dlg.py <mike@peacecorps.org.cv>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mnemosyne.libmnemosyne.component_manager import database
from ui_statistics_dlg import Ui_StatisticsDlg


class StatGraph(FigureCanvas):

    """Base canvas class for creating graphs with Matplotlib."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, color='white', 
                 scope=None):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=color, 
                     edgecolor=color)
        FigureCanvas.__init__(self, fig)
        #FigureCanvas.setSizePolicy(self, QSizePolicy.MinimumExpanding, 
                                   #QSizePolicy.MinimumExpanding)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        self.generate_figure(scope)
        #FigureCanvas.updateGeometry(self)

    def generate_figure(self, scope):
        pass


class ScheduleGraph(StatGraph):

    """Graph of card scheduling statistics."""

    def generate_figure(self, scope):

        """Create a bar graph of card scheduling statistics."""

        NDAYS = 7
        BAR_WIDTH = 1.0
        HALF_WIDTH = BAR_WIDTH / 2.0

        #self.axes.set_title('Scheduled cards for next week')
        self.axes.set_ylabel('Number of Cards Scheduled')
        self.axes.set_xlabel('Days')
        cards_per_day = []
        old_cumulative = 0
        for days in range(0, NDAYS):
            cumulative = database().scheduled_count(days)
            cards_per_day.append(cumulative - old_cumulative)
            old_cumulative = cumulative

        xticks = arange(NDAYS) + HALF_WIDTH
        bar_colors = ('r', 'g', 'b', 'c', 'm', 'y', 'k')
        self.axes.bar(xticks, cards_per_day, BAR_WIDTH, align='center', 
                      color=bar_colors, alpha=0.7, linewidth=0)
        self.axes.set_xticks(xticks)
        self.axes.set_xticklabels(('Today', '+1', '+2', '+3', '+4', '+5', '+6'), 
                                  fontsize='small')

        # Pad the right side of the graph if the last value is zero. Otheriwse,
        # the graph ends at the final xtick label, which looks ugly.
        if cards_per_day[-1] == 0:
            _, xmax = self.axes.set_xlim()
            self.axes.set_xlim(xmax=xmax+HALF_WIDTH)

        max_value = max(cards_per_day)
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
        from operator import add
        avg = lambda s: reduce(add, s) / len(s)
        if max(cards_per_day) == 0:
            # TODO (ma): print a message stating there are no stats rather than
            # displaying an empty graph.
            avg_height = 0
        else:
            avg_height = avg(filter(bool, cards_per_day))
        pad = avg_height * 1.05 - avg_height
        for i in range(0, NDAYS):
            height = cards_per_day[i]
            if height == 0: continue
            self.axes.text(xticks[i], height + pad, '%d' % height, ha='center', 
                           va='bottom', fontsize='small')


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
            grades[card.grade] += 1

        # TODO (ma): print a message stating there are no stats rather than
        # displaying an empty graph.
        if max(grades) == 0:
            return

        # Only print percentage on wedges > 5%.
        autopctfn = lambda x: '%1.1f%%' % x if x > 5 else ''
        self.axes.pie(grades, explode=(0.05, 0, 0, 0, 0, 0), autopct=autopctfn, 
                      labels=['Grade %d' % g if grades[g] > 0 else '' 
                              for g in range(0, len(grades))],
                      colors=('r', 'm', 'y', 'g', 'c', 'b'), shadow=True)
 


class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    def __init__(self, parent=None, name=None, modal=0):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.add_schedule_stats()

    def add_schedule_stats(self):
        bg_color = self.get_background_color()
        for scope in ('next_week', 'next_month', 'next_year', 'all_time'):
            parent = getattr(self, scope)
            layout_name = scope + '_layout'
            setattr(self, layout_name, QVBoxLayout(parent))
            layout = getattr(self, layout_name)
            layout.setObjectName(layout_name)
            graph_name = scope + '_graph'
            setattr(self, graph_name, ScheduleGraph(parent, scope=scope, 
                                                    color=bg_color))
            graph = getattr(self, graph_name)
            graph.setObjectName(graph_name)
            layout.addWidget(graph)

    def add_grades_stats(self):
        #self.all_categories = GradesGraph(self.grades_stack, color=graph_bg_color)
        #self.grades_stack_layout = QVBoxLayout(self.all_categories)
        #self.grades_stack_layout.addWidget(self.all_categories)
        pass

    def get_background_color(self):
        # Attempt to match the graph background color to the window. Sadly,
        # this won't work on OS X, XP, or Vista, since they use native theme
        # engines for drawing, rather than the palette. See:
        # http://doc.trolltech.com/4.4/qapplication.html#setPalette
        if self.style().objectName() == 'macintosh (Aqua)':
            bg_color = '0.91'
        else:
            r, g, b, _ = self.palette().color(self.backgroundRole()).getRgb()
            bg_color = map(lambda x: x / 255.0, (r, g, b))
        return bg_color
