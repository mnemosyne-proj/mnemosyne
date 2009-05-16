#
# add_menu_item_plugin.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.component_manager import main_widget
from mnemosyne.libmnemosyne.component_manager import component_manager


class HelloWorldPlugin(Plugin):
    
    name = "Hello world"
    description = "Add a menu item to the help menu"

    def __init__(self):
        Plugin.__init__(self)        
        self.action_hello = None

    def activate(self):
        Plugin.activate(self)
        self.action_hello = QtGui.QAction(main_widget())
        self.action_hello.setText("Hello world")
        main_widget().menu_Help.addAction(self.action_hello)
        QtCore.QObject.connect(self.action_hello, QtCore.SIGNAL("activated()"),
                               self.hello_world)

    def deactivate(self):
        Plugin.deactivate(self)
        if self.action_hello:
            main_widget().menu_Help.removeAction(self.action_hello)
            self.actionHello = None

    def hello_world(self):
        main_widget().information_box("Hi there!")        

component_manager.register(HelloWorldPlugin())

