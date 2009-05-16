#
# add_menu_item.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.component_manager import main_widget

# Quick and dirty version, does not use a plugin and therefore not be
# deactivated once the program is running.

def hello_world():
        main_widget().information_box("Hi there!") 

action_hello = QtGui.QAction(main_widget())
action_hello.setText("Hello world")
main_widget().menu_Help.addAction(action_hello)
QtCore.QObject.connect(action_hello, QtCore.SIGNAL("activated()"),
                       hello_world)
