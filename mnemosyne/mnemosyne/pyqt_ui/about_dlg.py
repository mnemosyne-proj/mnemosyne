#
# about_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.version import version
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_about_dlg import Ui_AboutDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import AboutDialog


class AboutDlg(QtWidgets.QDialog, Ui_AboutDlg, AboutDialog):

    def __init__(self, component_manager):
        super().__init__(self.main_widget(), component_manager=component_manager)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        # Note: the svg file does not seem to work under windows.
        #watermark = QtGui.QPixmap(":/mnemosyne/pixmaps/mnemosyne.svg").\
        #    scaledToHeight(200, QtCore.Qt.SmoothTransformation)
        watermark = QtGui.QPixmap(":/mnemosyne/pixmaps/mnemosyne.png")
        self.watermark.setPixmap(watermark)
        self.about_label.setText("<b>" + _("Mnemosyne") + " " + version + "</b><br><br>" + \
           _("Main author: Peter Bienstman") + "<br><br>" + \
           _("""Invaluable contributions from many people are acknowledged <a href="http://www.mnemosyne-proj.org/contributing.php">here</a>.""") + "<br><br>" + \
           _("""Go to <a href="http://www.mnemosyne-proj.org">http://www.mnemosyne-proj.org</a> for more information and source code."""))

    def activate(self):
        AboutDialog.activate(self)
        self.show()
