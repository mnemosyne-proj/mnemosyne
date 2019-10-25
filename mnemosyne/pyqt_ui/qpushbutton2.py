#
# qpushbutton2.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtGui, QtWidgets


class QPushButton2(QtWidgets.QPushButton):

    """QPushButton which throws away key repeats."""

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            return QtWidgets.QPushButton.keyPressEvent(self, event)
