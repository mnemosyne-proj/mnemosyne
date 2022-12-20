#
# qpushbutton2.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtGui, QtWidgets


class QPushButton2(QtWidgets.QPushButton):

    """QPushButton which throws away key repeats."""

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            return QtWidgets.QPushButton.keyPressEvent(self, event)
