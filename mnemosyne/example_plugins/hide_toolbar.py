#
# hide_toolbar.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui

from mnemosyne.libmnemosyne.plugin import Plugin


class HideToolbarPlugin(Plugin):

    name = "Hide toolbar"
    description = "Hide the main toolbar"
    supported_API_level = 3

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)

    def activate(self):
        Plugin.activate(self)
        self.main_widget().tool_bar.setVisible(False)

    def deactivate(self):
        Plugin.deactivate(self)
        self.main_widget().tool_bar.setVisible(True)


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(HideToolbarPlugin)

