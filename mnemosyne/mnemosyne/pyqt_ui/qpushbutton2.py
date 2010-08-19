#
# qpushbutton2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _


class QPushButton2(QtGui.QPushButton):

    """QPushButton which throws away key repeats.""" 

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            return QtGui.QPushButton.keyPressEvent(self, event)
