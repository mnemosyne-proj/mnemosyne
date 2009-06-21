#
# custom_statistics_page_widget.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.ui_component import UiComponent
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


# The statistics page.

class MyStatisticsPage(StatisticsPage):

    name = "My statistics"
        
    def prepare(self, variant):
        self.widget.setText("Hello world!")


# The custom widget.

class MyWidget(QtGui.QLabel, UiComponent):

    used_for = MyStatisticsPage
    instantiate = UiComponent.LATER


# Wrap it into a Plugin and then register the Plugin.

class CustomStatisticsWidgetPlugin(Plugin):
    name = "Custom statistics widget"
    description = "Example plugin for custom statistics widget"
    components = [MyStatisticsPage, MyWidget]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(CustomStatisticsWidgetPlugin)

