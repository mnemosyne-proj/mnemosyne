#
# lock_down.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.plugin import Plugin


class LockDownPlugin(Plugin):

    name = "Lock down the UI"
    description = "Hides the menu bar and the icon bar. The only way to remove this plugin later is by deleting 'lock_down.py' from Mnemosyne's plugin directory'"
    supported_API_level = 3
    
    def activate(self):
        Plugin.activate(self)
        self.main_widget().menuBar().hide()
        self.main_widget().tool_bar.hide()

    def deactivate(self):
        Plugin.deactivate(self)
        self.main_widget().menuBar().show()
        self.main_widget().findChild(QtWidgets.QToolBar).show()
        self.main_widget().tool_bar.show()


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(LockDownPlugin)

