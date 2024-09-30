#
# about_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.version import version
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_about_dlg import Ui_AboutDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import AboutDialog


class AboutDlg(QtWidgets.QDialog, AboutDialog, Ui_AboutDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        # Note: the svg file does not seem to work under windows.
        #watermark = QtGui.QPixmap("pixmaps/mnemosyne.svg").\
        #    scaledToHeight(200, QtCore.Qt.TransformationMode.SmoothTransformation)
        watermark = QtGui.QPixmap("icons:mnemosyne.png")
        self.watermark.setPixmap(watermark)
        self.about_label.setText("<b>" + _("Mnemosyne") + " " + version + "</b><br><br>" + \
           _("Main author: Peter Bienstman") + "<br><br>" + \
           _("""Invaluable contributions from many people are acknowledged <a href="http://www.mnemosyne-proj.org/contributing.php">here</a>.""") + "<br><br>" + \
           _("""Go to <a href="http://www.mnemosyne-proj.org">http://www.mnemosyne-proj.org</a> for more information and source code."""))

    def activate(self):
        AboutDialog.activate(self)
        self.exec()
        #self.show()
