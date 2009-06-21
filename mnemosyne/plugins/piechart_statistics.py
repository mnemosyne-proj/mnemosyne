#
# piechart_statistics.py <Peter.Bienstman@UGent.be>, <mike@peacecorps.org.cv>
#

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


# The piechart statistics page.

class GradesPiechart(StatisticsPage):

    name = "Grades piechart"
        
    def prepare(self, variant):                
        self.plot_type = "piechart"
        self.title = "Number of cards"
        self.data = []
        for grade in range (-1,6):
            self.data.append(self.database().con.execute(\
                "select count() from cards where grade=? and active=1",
                 (grade, )).fetchone()[0])
        self.extra_hints["labels"] = ["Unseen" if self.data[0] > 0 else ""] +\
          ["Grade %d" % (g-1) if self.data[g] > 0 else "" for g in range(1, 7)]
        self.extra_hints["colors"] = ["w", "r", "m", "y", "g", "c", "b"]
        self.extra_hints["shadow"] = True
        

# Wrap it into a Plugin and then register the Plugin.

class PiechartPlugin(Plugin):
    name = "Piechart grades"
    description = "Show the grade statistics in a piechart"
    components = [GradesPiechart]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(PiechartPlugin)

