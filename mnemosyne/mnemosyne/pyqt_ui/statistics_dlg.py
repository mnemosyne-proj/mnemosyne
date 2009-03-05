#
# statistics_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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

class StatisticsDlg(QDialog, Ui_StatisticsDlg):

    def __init__(self, parent=None, name=None, modal=0):
        QDialog.__init__(self,parent)
        self.setupUi(self)

        # Schedule information.

        text = self.trUtf8("Scheduled cards for next week:\n\n")

        old_cumulative = 0
        for days in range(0,8):
            cumulative = database().scheduled_count(days)
            text.append(self.trUtf8("In")).\
                 append(QString(" " + str(days) + " ")).\
                 append(self.trUtf8("day(s) :")).\
                 append(QString(" " + str(cumulative-old_cumulative) + "\n"))
            old_cumulative = cumulative

        self.schedule_info.setText(text)

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

