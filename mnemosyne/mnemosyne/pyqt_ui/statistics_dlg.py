##############################################################################
#
# Widget to show basic statistics
#
# <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from statistics_frm import *



##############################################################################
#
# ListItem
#
##############################################################################

class ListItem(QListViewItem):
    def __init__(self, parent, name, number):
        QListViewItem.__init__(self, parent, name, str(number))
        self.setMultiLinesEnabled(1)
        
    def compare(self, item, column, ascending):
        if column == 0:
            return self.key(0,ascending).compare(item.key(0,ascending))
        else: # Funny casts for Windows compatibility.
            return int(str(self.text(1))) - int(str(item.text(1)))


        
##############################################################################
#
# StatisticsDlg
#
##############################################################################

class StatisticsDlg(StatisticsFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0):
        
        StatisticsFrm.__init__(self,parent,name,modal,
                              Qt.WStyle_MinMax | Qt.WStyle_SysMenu)

        # Schedule information.

        text = "Scheduled cards for the next days:\n\n"

        old_cumulative = 0
        for days in range(0,8):
            cumulative = scheduled_items(days)
            text += "In " + str(days) + " day(s) : " \
                    + str(cumulative - old_cumulative) + "\n"
            old_cumulative = cumulative
            
        self.schedule_info.setText(text)

        # Grade information.

        text = "Number of cards with the following grades:\n\n"

        grades = [0, 0, 0, 0, 0, 0]
        for item in get_items():
            if item.is_in_active_category():
                grades[item.grade] += 1

        norm = sum(grades)
        if norm == 0:
            norm = 1 # Avoid division by zero.

        for grade in range(0,6):
            text += "Grade " + str(grade) + " : " \
                    + str(grades[grade]) + " ("\
                    + ("%.1f" % (100.*grades[grade] / norm)) + " %)\n"
        
        self.grades_info.setText(text)

        # Category information.

        categories = {}
        for item in get_items():
            name = item.cat.name
            if name not in categories.keys():
                categories[name] = 1
            else:
                categories[name] += 1

        for cat in categories.keys():
            ListItem(self.category_info, cat, categories[cat])
       
