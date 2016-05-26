#
# add_menu_item.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui

from mnemosyne.libmnemosyne.plugin import Plugin


class HelloWorldPlugin(Plugin):
    
    name = "Hello world"
    description = "Add a menu item to the help menu"

    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        self.action_hello = None

    def activate(self):
        Plugin.activate(self)
        self.action_hello = QtGui.QAction(self.main_widget())
        self.action_hello.setText("Hello world")
        self.main_widget().menu_Help.addAction(self.action_hello)
        QtCore.QObject.connect(self.action_hello, QtCore.SIGNAL("activated()"),
                               self.hello_world)

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

