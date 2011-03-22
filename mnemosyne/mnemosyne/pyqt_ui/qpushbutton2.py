#
# qpushbutton2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui


class QPushButton2(QtGui.QPushButton):

    """QPushButton which throws away key repeats."""

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            return QtGui.QPushButton.keyPressEvent(self, event)
