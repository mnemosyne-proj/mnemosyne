#
# custom_statistics_page_widget.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage
from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
     StatisticsWidget


# The statistics page.

class MyStatisticsPage(StatisticsPage):

    name = "My statistics"
        
    def prepare_statistics(self, variant):
        self.text = "Hello world!"


# The custom widget.

class MyStatisticsWidget(QtGui.QLabel, StatisticsWidget):

    used_for = MyStatisticsPage

    def __init__(self, parent, component_manager, page):
        QtGui.QLabel.__init__(self, parent)
        StatisticsWidget.__init__(self, component_manager)
        self.page = page

    def show_statistics(self):
        self.setText(self.page.text)


# Wrap it into a Plugin and then register the Plugin.

class CustomStatisticsWidgetPlugin(Plugin):
    name = "Custom statistics widget"
    description = "Example plugin for custom statistics widget"
    components = [MyStatisticsPage, MyStatisticsWidget]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(CustomStatisticsWidgetPlugin)

