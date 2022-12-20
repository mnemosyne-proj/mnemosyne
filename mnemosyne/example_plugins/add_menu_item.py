#
# add_menu_item.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.plugin import Plugin


class HelloWorldPlugin(Plugin):
    
    name = "Hello world"
    description = "Add a menu item to the help menu"
    supported_API_level = 3

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.action_hello = None

    def activate(self):
        Plugin.activate(self)
        self.action_hello = QtGui.QAction(self.main_widget())
        self.action_hello.setText("Hello world")
        self.main_widget().menu_Help.addAction(self.action_hello)
        self.action_hello.triggered.connect(self.hello_world)

    def deactivate(self):
        Plugin.deactivate(self)
        if self.action_hello:
            self.main_widget().menu_Help.removeAction(self.action_hello)
            self.actionHello = None

    def hello_world(self):
        self.main_widget().show_information("Hi there!")        

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(HelloWorldPlugin)

