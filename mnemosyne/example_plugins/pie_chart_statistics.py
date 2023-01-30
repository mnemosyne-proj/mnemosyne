#
# pie_chart_statistics.py <Peter.Bienstman@gmail.com>, <mike@peacecorps.org.cv>
#

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import PlotStatisticsPage
from mnemosyne.pyqt_ui.statistics_wdgts_plotting import PlotStatisticsWdgt

# The piechart statistics page (GUI independent part).

class MyGrades(PlotStatisticsPage):

    name = "Grades pie chart"

    def prepare_statistics(self, variant):
        self.x = list(range(-1, 6))
        self.y = []
        for grade in self.x:
            self.y.append(self.database().con.execute(\
                "select count() from cards where grade=? and active=1",
                 (grade, )).fetchone()[0])

# The custom widget.

class PieChartWdgt(PlotStatisticsWdgt):

    used_for = MyGrades

    def show_statistics(self, variant):
        if not self.page.y:
            self.display_message(_("No stats available."))
            return
        self.activate()
        # Pie charts look better on a square canvas.
        self.axes.set_aspect('equal')
        labels = ["Unseen" if self.page.y[0] > 0 else ""] + \
            ["Grade %d" % (g-1) if self.page.y[g] > 0 \
            else "" for g in range(1, 7)]
        colors = ["w", "r", "m", "y", "g", "c", "b"]
        # Only print percentage on wedges > 5%.
        autopct = lambda x: "%1.1f%%" % x if x > 5 else ""
        self.axes.pie(self.page.y, labels=labels, colors=colors,
                      shadow=True, autopct=autopct)
        self.axes.set_title("Number of cards")

# Wrap it into a Plugin and then register the Plugin.

class PieChartPlugin(Plugin):
    name = "Pie chart grades"
    description = "Show the grade statistics in a pie chart"
    components = [MyGrades, PieChartWdgt]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(PieChartPlugin)

