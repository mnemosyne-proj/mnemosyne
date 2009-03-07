#
# statistics_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from numpy import arange
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mnemosyne.libmnemosyne.component_manager import database
from ui_statistics_dlg import Ui_StatisticsDlg

#class ListItem(QListViewItem):#{{{
#    def __init__(self, parent, name, number):
#        QListViewItem.__init__(self, parent, name, str(number))
#        self.setMultiLinesEnabled(1)

#    def compare(self, item, column, ascending):
#        if column == 0:
#            return self.key(0,ascending).compare(item.key(0,ascending))
#        else: # Funny casts for Windows compatibility.
#            return int(str(self.text(1))) - int(str(item.text(1)))
#}}}


class MplCanvas(FigureCanvas):
     """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
     def __init__(self, parent=None, width=5, height=4, dpi=100):
         fig = Figure(figsize=(width, height), dpi=dpi)
         self.axes = fig.add_subplot(111)
         #self.axes.hold(False)
         self.generate_figure()
         FigureCanvas.__init__(self, fig)
         self.setParent(parent)
         FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, 
                                    QSizePolicy.Expanding)
         FigureCanvas.updateGeometry(self)

    def generate_graph():
        pass

class ScheduleGraph(MplCanvas):
    """Graph of card scheduling statistics"""
    def generate_graph():
        cards_per_day = []
        old_cumulative = 0
        for days in range(0,8):
            cumulative = database().scheduled_count(days)
            cards_per_day.append(cumulative - old_cumulative)
            old_cumulative = cumulative
        self.axes.plot([1,2,3,4,5])


class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    def __init__(self, parent=None, name=None, modal=0):
        QDialog.__init__(self,parent)
        self.setupUi(self)

        # Schedule information.

        self.sched_widget = QWidget(self)
        self.sched_layout = QVBoxLayout(self.sched_widget)
        self.sched_canvas = ScheduleGraph(self.sched_widget, width=5, height=4, dpi=100)
        self.sched_layout.addWidget(self.sched_canvas)


        # Grade information.

        text = self.trUtf8("Number of cards with the following grades:\n\n")
 
        grades = [0, 0, 0, 0, 0, 0]
        for card in database().cards:
            # TODO: Only include stats from cards with active categories.
            #if card.fact.cat[0].active:
                grades[card.grade] += 1
 
        norm = sum(grades)
        if norm == 0:
            norm = 1 # Avoid division by zero.
 
        for grade in range(0,6):
            text.append(self.trUtf8("Grade")).\
                 append(QString(" " + str(grade) + " : " \
                    + str(grades[grade]) + " ("\
                    + ("%.1f" % (100.*grades[grade] / norm)) + " %)\n"))
 
        self.grades_info.setText(text)

#        # Category information.

#        categories = {}
#        for item in get_items():
#            name = item.cat.name
#            if name not in categories.keys():
#                categories[name] = 1
#            else:
#                categories[name] += 1

#        for cat in categories.keys():
#            ListItem(self.category_info, cat, categories[cat])

